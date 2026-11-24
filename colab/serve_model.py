"""Colab-hosted Semicon.AI inference service.

Set BASE_MODEL_ID, LORA_ADAPTER_PATH and SEMICON_MODEL_API_TOKEN in the
Colab environment before launching. Mount Google Drive in the notebook first.
Do not commit adapter weights or API tokens to Git.
"""
import os
import secrets
from typing import Literal

import torch
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

BASE_MODEL_ID = os.environ.get("BASE_MODEL_ID", "").strip()
LORA_ADAPTER_PATH = os.environ.get("LORA_ADAPTER_PATH", "").strip()
API_TOKEN = os.environ.get("SEMICON_MODEL_API_TOKEN", "").strip()
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", "768"))

if not BASE_MODEL_ID or not LORA_ADAPTER_PATH or not API_TOKEN:
    raise RuntimeError(
        "Set BASE_MODEL_ID, LORA_ADAPTER_PATH and SEMICON_MODEL_API_TOKEN before starting."
    )
if not torch.cuda.is_available():
    raise RuntimeError("A CUDA GPU is required for this Colab inference configuration.")

app = FastAPI(title="Semicon.AI Colab Model Service", version="2.0.0-alpha")

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

quantization = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    quantization_config=quantization,
    device_map="auto",
    torch_dtype=torch.float16,
)
model = PeftModel.from_pretrained(base_model, LORA_ADAPTER_PATH)
model.eval()


class GenerateRequest(BaseModel):
    specification: str = Field(min_length=5, max_length=12000)
    hdl: Literal["verilog", "vhdl"] = "verilog"
    module_name: str | None = Field(default=None, max_length=128)
    constraints: list[str] = Field(default_factory=list, max_length=30)


class GenerateResponse(BaseModel):
    hdl: str
    code: str
    model: str


def authorize(authorization: str | None = Header(default=None)):
    expected = f"Bearer {API_TOKEN}"
    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True, "device": "cuda"}


@app.post("/v1/generate", response_model=GenerateResponse, dependencies=[Depends(authorize)])
def generate(request: GenerateRequest):
    # Keep this prompt format aligned with the format used during LoRA fine-tuning.
    # If training used a different template, change this function to match it.
    language = "Verilog" if request.hdl == "verilog" else "VHDL"
    constraints = "\n".join(f"- {item}" for item in request.constraints) or "- No additional constraints"
    module_line = f"Module/entity name: {request.module_name}\n" if request.module_name else ""
    instruction = (
        f"{module_line}Specification: {request.specification}\n"
        f"Design constraints:\n{constraints}\n"
        f"Return only synthesizable {language} source code."
    )
    # Preserve the Verilog template observed in the existing Demo_7 notebook.
    # VHDL is an experimental prompt path and must be evaluated independently.
    prompt = (
        f"### Instruction:\n{instruction}\n\n### Verilog:\n"
        if request.hdl == "verilog"
        else f"### Instruction:\n{instruction}\n\n### VHDL:\n"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = output[0][inputs["input_ids"].shape[1]:]
    code = tokenizer.decode(generated, skip_special_tokens=True).strip()
    if not code:
        raise HTTPException(status_code=502, detail="Model returned empty RTL.")
    return GenerateResponse(hdl=request.hdl, code=code, model=BASE_MODEL_ID)
