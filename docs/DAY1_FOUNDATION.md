# Semicon.AI 2.0 — Day 1 foundation

## Decisions

- Preserve the existing notebooks and trained LoRA adapter.
- Keep the model weights in Google Drive; do not put weights or credentials in Git.
- Use Colab GPU as the initial inference host.
- Expose model inference through a small authenticated HTTP service.
- Keep the main FastAPI gateway independent of Colab.
- Treat Verilog and VHDL as separate generation and verification paths.

## Added in this branch

- `backend/app`: FastAPI gateway with health and RTL-generation endpoints.
- `colab/serve_model.py`: Colab GPU model-serving scaffold for the existing adapter.
- `colab/README.md`: setup instructions and required compatibility checks.
- `backend/.env.example`: names of private backend configuration values.
- `docs/DAY1_FOUNDATION.md`: architecture and next steps.

## Day 1 acceptance checks

1. Confirm the exact base-model ID in the existing notebook.
2. Confirm the exact adapter directory in Google Drive.
3. Confirm the adapter loads successfully on the available Colab GPU.
4. Align the serving prompt with the original fine-tuning prompt format.
5. Generate one Verilog and one VHDL sample and save the raw outputs.
6. Start the FastAPI gateway and verify `GET /health`.
7. Verify that `POST /v1/generate` forwards requests and rejects an unconfigured model endpoint.

## Known limitations

- This commit is a foundation scaffold, not a completed or tested deployment.
- The current model adapter's VHDL capability is unknown.
- The inference endpoint requires a secure private tunnel from the backend to Colab.
- RTL output is not considered correct or verified merely because generation succeeds.
- The HDL execution/sandbox service will be implemented in a later phase.
