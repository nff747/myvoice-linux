<div align="center">
  <img src="https://raw.githubusercontent.com/user/myvoice-linux/main/assets/banner.png" alt="MyVoice TTS Linux Banner" width="100%" />
  
  <h1>🎙️ MyVoice TTS (Linux Edition)</h1>
  <p><strong>The ultimate, lightning-fast AI Voice Generator & Cloner tailored for Linux.</strong></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Platform: Linux](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-success)](#)
  [![GPU: NVIDIA](https://img.shields.io/badge/GPU-CUDA%20%2F%20RTX-76B900)](#)
</div>

---

## 🌟 What is MyVoice TTS?
MyVoice TTS is a state-of-the-art text-to-speech application specifically optimized for real-time voice chat, streaming, and content creation. This repository hosts the **Linux-first port**, featuring deep architectural changes to maximize performance on NVIDIA GPUs via PyTorch 2.6 and CUDA 12.4.

Whether you're looking to generate expressive character voices or instantly clone a custom voice for Discord, MyVoice delivers zero-shot streaming inference so fast that the AI speaks the *moment* you hit Enter.

---

## ✨ Key Features

- **⚡ Instant Streaming Inference**: Uses Flash-Attention and `torch.compile` Triton kernels to deliver sub-second generation times. Type and talk instantly.
- **🎭 Controllable Emotions**: Generate speech with dynamic emotion tags (Happy, Angry, Sad, Flirtatious). *Note: Supported natively via the UI on VoiceDesign profiles.*
- **🗣️ Zero-Shot Voice Cloning**: Upload a 5-second clean audio sample and perfectly clone any voice.
- **🎙️ Seamless Virtual Mic Routing**: Routes audio directly to PulseAudio / PipeWire virtual sinks to effortlessly pipe AI voices into Discord, OBS, or Zoom.
- **💻 Polished Modern UI**: Sleek, fully-responsive dark mode UI built with PyQt6.

## 🚀 Installation & Setup (Linux)

### Prerequisites
- NVIDIA GPU (RTX 30XX / 40XX series recommended)
- NVIDIA Drivers installed
- `uv` (Fast Python package installer)

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/myvoice-linux.git
cd myvoice-linux

# 2. Create the environment and install PyTorch with CUDA support
uv venv
uv pip install -r requirements.txt
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 3. Launch the App
./run_myvoice.sh
```

*(Note: The very first generation will take 1-3 minutes while PyTorch compiles the model specifically for your GPU. All subsequent generations will be instantaneous.)*

---

## 🎨 UI & Screenshots

<div align="center">
  <img src="https://raw.githubusercontent.com/user/myvoice-linux/main/assets/ui_showcase.png" alt="Sleek Dark UI" width="800px" />
  <p><em>Modern, distraction-free interface with single-click emotion controls.</em></p>
</div>

---

## 🧠 Model Architecture & Tiers

We utilize the incredibly powerful **Qwen3-TTS** foundation models:
1. **Quality Tier (1.7B Parameters)**: Best for high-fidelity emotion control and accurate voice cloning. Requires ~4-8GB VRAM.
2. **Small Tier (0.6B Parameters)**: Extremely lightweight and incredibly fast. Best for older laptops or CPU-only constraints.

---

## ⚖️ License & Attribution
This project is an unofficial Linux-focused port of the original MyVoice software. The foundational codebase and original GUI architecture belong to the original creators. 

Released under the **MIT License**. Please see the `LICENSE` file for full copyright notices and permissions.

### Special Thanks
- **Qwen3-TTS Team**: For their groundbreaking open-source foundational text-to-speech models.
- **Original MyVoice Devs**: For the excellent Qt application framework.
