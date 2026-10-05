#!/bin/bash
echo "Waiting for PyTorch to finish installing..."
wait $(pgrep -f "uv pip install torch")
echo "Installing flash-attn..."
uv pip install flash-attn --no-build-isolation
echo "GPU Support Installed Successfully!"
