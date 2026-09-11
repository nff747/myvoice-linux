#!/bin/bash
while true; do
  clear
  echo "MyVoice Background Download Progress"
  echo "===================================="
  echo "Downloading the 1.7B High Quality model files..."
  du -sh ~/.cache/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-1.7B-Base 2>/dev/null || echo "Waiting to start..."
  echo "(Total size will be around 4.5 GB. It will resume where it left off!)"
  sleep 5
done
