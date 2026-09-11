# Contributing to MyVoice (Linux Edition)

We welcome contributions from the open-source community! Whether you are fixing bugs, optimizing inference speeds, improving the UI, or adding new features, your help is appreciated.

## Getting Started

1. **Fork the Repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/<your-username>/myvoice-linux.git
   cd myvoice-linux
   ```
3. **Set up the virtual environment**:
   ```bash
   uv venv
   uv pip install -r requirements.txt
   uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

## Development Guidelines

- **Code Style**: Follow PEP 8 guidelines. Keep code clean, modular, and well-typed.
- **Audio Routing**: Any audio streaming changes must maintain compatibility with PipeWire / PulseAudio.
- **Pull Requests**:
  - Keep PRs focused on a single topic or feature.
  - Describe your changes and test results clearly in the PR description.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
