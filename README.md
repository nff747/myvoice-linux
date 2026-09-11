<div align="center">
  <h1>🎙️ MyVoice (Linux Edition)</h1>
  <p><strong>Open-Source, Low-Latency AI Voice Generator, Voice Cloner & Auto-Reply Call Assistant.</strong></p>
  <p><em>Originally forked and completely overhauled for Linux & CUDA by <a href="https://github.com/nff747">@nff747</a></em></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Platform: Linux](https://img.shields.io/badge/Platform-Linux%20(Arch%20%2F%20Ubuntu%20%2F%20Fedora)-success)](#)
  [![GPU: NVIDIA](https://img.shields.io/badge/GPU-CUDA%2012.4%20%2F%20RTX%20Accelerated-76B900)](#)
  [![TTS: Qwen3--TTS](https://img.shields.io/badge/Model-Qwen3--TTS%201.7B-orange)](#)
  [![Audio: PipeWire](https://img.shields.io/badge/Audio-PipeWire%20%2F%20PulseAudio-blueviolet)](#)
</div>

---

## 🌟 About This Project

This repository is an **open-source, Linux-first reimagining** of MyVoice. While built on the foundation of the original concept, the codebase has undergone a **massive architectural rework** by [@nff747](https://github.com/nff747) to eliminate Windows-specific bottlenecks, introduce native PipeWire virtual routing, accelerate inference on NVIDIA GPUs, and add an autonomous **AI Auto-Reply Mode** for live calls and Discord VC.

---

## 🚀 Major Upgrades in this Linux Edition (by @nff747)

### 1. 🤖 Autonomous AI Auto-Reply Mode (Discord & Calls)
- **Live Voice Activity Detection (VAD)**: Listens to incoming caller speech with rolling pre-buffers to never clip words.
- **In-Memory GPU Whisper**: Zero-disk I/O Whisper transcription running directly on CUDA in **<25ms**.
- **LLM Reasoning**: Plugs into local LiteLLM/Ollama, OpenCode, OpenAI, or Gemini APIs to generate intelligent, context-aware replies.
- **Instant Dual-Routing**: Speaks the AI response through your cloned voice directly into the Discord voice channel.

### 2. ⚡ Sub-Second GPU Inference (PyTorch 2.6 + CUDA 12.4)
- Upgraded to modern CUDA 12.4 and PyTorch 2.6 with native `torch.compile` Triton streaming kernels.
- Supports `bfloat16` precision for maximum throughput on RTX 30xx/40xx/50xx GPUs.
- `TRUE_STREAM` progressive chunk decoding begins playing audio the millisecond tokens are generated.

### 3. 🎙️ Native Linux PipeWire & PulseAudio Dual-Stream Engine
- Replaced Windows-only audio hooks with automated PipeWire null-sinks and remapped virtual microphones.
- Simultaneous playback: Listen to your voice locally through headphones while simultaneously streaming to Discord with **zero echo or double voice**.

### 4. 🎨 Redesigned Modern UI/UX
- GitHub-inspired dark mode interface (`#0d1117` palette).
- Clickable voice selector + prominent **`+ Clone`** shortcut button for instant voice uploading.
- Real-time status indicators for Auto Mode (`Listening`, `Hearing`, `Thinking`, `Speaking`).

---

## 🛠️ Quick Start & Installation

### Prerequisites
- **Linux** (Arch/CachyOS, Ubuntu, Debian, Fedora, etc.)
- **NVIDIA GPU** with proprietary drivers (RTX 30XX / 40XX series recommended)
- **PipeWire / PulseAudio** installed
- **`uv`** package manager (recommended for blazing fast install)

```bash
# 1. Clone the repository
git clone https://github.com/nff747/myvoice-linux.git
cd myvoice-linux

# 2. Create Python virtual environment
uv venv

# 3. Install core dependencies
uv pip install -r requirements.txt

# 4. Install CUDA-accelerated PyTorch
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 5. Run MyVoice!
./run_myvoice.sh
```

*(Note: The very first generation will take 1–3 minutes while PyTorch compiles the GPU kernels for your hardware. All subsequent generations will be instantaneous.)*

---

## 🎧 Discord & Call Setup Guide

1. Launch MyVoice via `./run_myvoice.sh` (this automatically creates the `MyVoice_Virtual_Microphone` device).
2. Open **Discord → User Settings → Voice & Video**:
   * **Microphone (Input Device)**: Select **`MyVoice_Virtual_Microphone`**
   * **Speaker (Output Device)**: Select your **Headphones / Speakers** (e.g. `Ryzen HD Audio` / `Default`)
3. In MyVoice, type your text and press **Enter**, or toggle **`🤖 Auto`** to let the AI talk in your voice!

---

## 🤝 Contributing

Contributions from the open-source community are welcome!
1. Fork the repo.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## ⚖️ License & Open-Source Attribution

This project is licensed under the **[MIT License](LICENSE)** — free and open for everyone to use, modify, and distribute.

- **Linux Port, AI Auto-Reply & Major Enhancements**: [@nff747](https://github.com/nff747)
- **Original GUI Foundation**: Original MyVoice Team
- **Foundational Models**: Qwen3-TTS by Alibaba Qwen Team & OpenAI Whisper
