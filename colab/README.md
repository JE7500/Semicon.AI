# Colab model service

This service loads the existing CodeLlama base model and the LoRA adapter from Google Drive.
It is intentionally separate from the main API so that the UI and verification services do
not depend on a Colab-specific runtime.

## 1. Prepare a Colab notebook

Run:

```python
from google.colab import drive
drive.mount("/content/drive")
```

Install dependencies:

```bash
!pip install -r /content/Semicon.AI/colab/requirements.txt
```

Clone the repository or upload this folder into the Colab runtime first.

## 2. Configure environment variables

Use the exact base-model ID and adapter directory from the existing training/inference notebook.
Do not assume the model ID or adapter path; verify both in the notebook and in Google Drive.

```python
import os, secrets
os.environ["BASE_MODEL_ID"] = "REPLACE_WITH_THE_EXACT_BASE_MODEL_ID"
os.environ["LORA_ADAPTER_PATH"] = "/content/drive/MyDrive/REPLACE_WITH_ADAPTER_DIRECTORY"
os.environ["SEMICON_MODEL_API_TOKEN"] = secrets.token_urlsafe(32)
```

Keep the generated token in the backend's private environment as `SEMICON_MODEL_API_TOKEN`.
Never commit it, paste it into public notebooks, or expose it in frontend JavaScript.

## 3. Start the inference service

```bash
!uvicorn serve_model:app --host 0.0.0.0 --port 8000
```

Expose the port only through a private/authenticated tunnel. Set the resulting private service
URL as `SEMICON_MODEL_ENDPOINT` in the backend environment.

## Important compatibility check

The prompt in `serve_model.py` is a safe initial template, not a confirmed match for the
original fine-tuning data format. Before comparing output quality, inspect the original
training notebook and align the prompt exactly with the training template. Test Verilog and
VHDL independently; the existing adapter's VHDL capability is not established by this scaffold.
