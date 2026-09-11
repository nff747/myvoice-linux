"""
Auto-Reply AI Settings Panel

Configuration panel for automated voice call and Discord VC AI replies:
- Master activation toggle
- Customizable greeting announcement
- AI Persona / System Prompt definition
- LLM API endpoint (LiteLLM, OpenAI, Gemini, OpenCode, Ollama)
- Model selection and VAD sensitivity parameters
"""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from myvoice.models.app_settings import AppSettings

_logger = logging.getLogger(__name__)


class AutoReplySettingsPanel(QWidget):
    """Settings widget for the Auto-Reply AI call feature."""

    settings_changed = pyqtSignal()

    def __init__(
        self,
        app_settings: Optional[AppSettings] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._app_settings = app_settings

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # ── 1. General & Persona Group ──
        persona_group = QGroupBox("Auto-Reply AI Persona")
        persona_form = QFormLayout(persona_group)

        self.enable_checkbox = QCheckBox("Enable Auto-Reply Mode")
        self.enable_checkbox.setToolTip(
            "When enabled, listens to incoming voice audio, generates an AI response, and speaks it automatically."
        )
        self.enable_checkbox.toggled.connect(self._on_field_changed)
        persona_form.addRow(self.enable_checkbox)

        self.greeting_edit = QLineEdit()
        self.greeting_edit.setPlaceholderText("This call is now set to automated AI mode.")
        self.greeting_edit.setToolTip("Spoken by the TTS voice the moment auto-reply mode is engaged.")
        self.greeting_edit.textChanged.connect(self._on_field_changed)
        persona_form.addRow("Call Greeting:", self.greeting_edit)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText(
            "You are an AI assistant in a live voice call. Respond naturally, conversationally, concisely (1-2 sentences), and directly to what was said."
        )
        self.prompt_edit.setMinimumHeight(70)
        self.prompt_edit.setMaximumHeight(110)
        self.prompt_edit.textChanged.connect(self._on_field_changed)
        persona_form.addRow("AI System Prompt:", self.prompt_edit)

        layout.addWidget(persona_group)

        # ── 2. API & Model Configuration Group ──
        api_group = QGroupBox("AI Engine & API Configuration")
        api_form = QFormLayout(api_group)

        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("http://localhost:4000/v1")
        self.api_url_edit.setToolTip("OpenAI-compatible API base URL (LiteLLM, OpenAI, Ollama, OpenCode, etc.)")
        self.api_url_edit.textChanged.connect(self._on_field_changed)
        api_form.addRow("API Base URL:", self.api_url_edit)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("sk-...")
        self.api_key_edit.setToolTip("API Key (leave blank if your local server doesn't require one)")
        self.api_key_edit.textChanged.connect(self._on_field_changed)
        api_form.addRow("API Key:", self.api_key_edit)

        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("gemini-3.5-flash")
        self.model_edit.setToolTip("Model name to query (e.g. gemini-3.5-flash, gpt-4o-mini, llama3-os)")
        self.model_edit.textChanged.connect(self._on_field_changed)
        api_form.addRow("Model Name:", self.model_edit)

        layout.addWidget(api_group)

        # ── 3. Voice Activity Detection (VAD) Group ──
        vad_group = QGroupBox("Voice Detection (VAD)")
        vad_form = QFormLayout(vad_group)

        self.silence_spin = QDoubleSpinBox()
        self.silence_spin.setRange(0.5, 5.0)
        self.silence_spin.setSingleStep(0.1)
        self.silence_spin.setValue(1.5)
        self.silence_spin.setSuffix(" s")
        self.silence_spin.setToolTip("Duration of silence before the AI considers the speaker finished.")
        self.silence_spin.valueChanged.connect(self._on_field_changed)
        vad_form.addRow("Silence Pause Trigger:", self.silence_spin)

        self.energy_spin = QDoubleSpinBox()
        self.energy_spin.setRange(0.005, 0.200)
        self.energy_spin.setSingleStep(0.005)
        self.energy_spin.setDecimals(3)
        self.energy_spin.setValue(0.020)
        self.energy_spin.setToolTip("Microphone volume sensitivity threshold to distinguish speech from room noise.")
        self.energy_spin.valueChanged.connect(self._on_field_changed)
        vad_form.addRow("Sensitivity Threshold:", self.energy_spin)

        layout.addWidget(vad_group)
        layout.addStretch()

        if app_settings is not None:
            self.load_state(app_settings)

    def _on_field_changed(self, *args) -> None:
        self.settings_changed.emit()

    def load_state(self, settings: AppSettings) -> None:
        """Load state from AppSettings."""
        self._app_settings = settings
        self.blockSignals(True)
        try:
            self.enable_checkbox.setChecked(bool(settings.auto_reply_enabled))
            self.greeting_edit.setText(settings.auto_reply_greeting or "")
            self.prompt_edit.setPlainText(settings.auto_reply_system_prompt or "")
            self.api_url_edit.setText(settings.auto_reply_api_url or "")
            self.api_key_edit.setText(settings.auto_reply_api_key or "")
            self.model_edit.setText(settings.auto_reply_model or "")
            self.silence_spin.setValue(float(settings.auto_reply_silence_duration or 1.5))
            self.energy_spin.setValue(float(settings.auto_reply_energy_threshold or 0.02))
        finally:
            self.blockSignals(False)

    def save_state(self, settings: AppSettings) -> None:
        """Persist state to AppSettings."""
        settings.auto_reply_enabled = self.enable_checkbox.isChecked()
        settings.auto_reply_greeting = self.greeting_edit.text().strip()
        settings.auto_reply_system_prompt = self.prompt_edit.toPlainText().strip()
        settings.auto_reply_api_url = self.api_url_edit.text().strip()
        settings.auto_reply_api_key = self.api_key_edit.text().strip()
        settings.auto_reply_model = self.model_edit.text().strip()
        settings.auto_reply_silence_duration = float(self.silence_spin.value())
        settings.auto_reply_energy_threshold = float(self.energy_spin.value())
