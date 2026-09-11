"""
Auto-Reply AI Service Module

Provides intelligent real-time conversational auto-reply for voice calls and Discord VC:
1. Listens for speech using Voice Activity Detection (VAD) via microphone / audio input.
2. Transcribes caller speech using Whisper.
3. Queries an LLM backend (LiteLLM, OpenAI, Gemini, Ollama, OpenCode, or custom API).
4. Streams the AI-generated response through MyVoice's Qwen3-TTS into the virtual mic.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import tempfile
import threading
import time
import wave
from typing import Callable, Dict, List, Optional

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

from myvoice.models.app_settings import AppSettings


class AutoReplyService(QObject):
    """
    Service managing automated AI call answering and voice chat responses.
    """

    # Signals for UI updates
    status_changed = pyqtSignal(str, str)  # (status_key, display_message)
    transcription_ready = pyqtSignal(str)   # transcribed text from caller
    ai_response_ready = pyqtSignal(str)     # AI generated text response

    def __init__(
        self,
        settings: AppSettings,
        tts_callback: Optional[Callable[[str], None]] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = settings
        self._tts_callback = tts_callback

        self.is_active = False
        self.is_speaking = False
        self._stop_event = threading.Event()
        self._listener_thread: Optional[threading.Thread] = None

        # Conversation history for context (keeps last 6 turns)
        self.conversation_history: List[Dict[str, str]] = []

        # Whisper cache / instance
        self._whisper_model = None

    def set_tts_callback(self, callback: Callable[[str], None]) -> None:
        """Set the callback used to trigger TTS generation."""
        self._tts_callback = callback

    def update_settings(self, settings: AppSettings) -> None:
        """Update settings configuration."""
        self.settings = settings

    def set_speaking_state(self, speaking: bool) -> None:
        """
        Notify the service when TTS is actively playing audio.
        Prevents acoustic feedback / self-triggering while the AI is talking.
        """
        self.is_speaking = speaking
        if speaking:
            self.logger.debug("AutoReply: TTS is speaking — VAD input temporarily muted")

    def toggle(self) -> bool:
        """Toggle auto-reply mode on/off."""
        if self.is_active:
            self.stop()
            return False
        else:
            self.start()
            return True

    def start(self) -> None:
        """Start auto-reply mode."""
        if self.is_active:
            return

        self.is_active = True
        self._stop_event.clear()

        # Reset conversation history for new session
        self.conversation_history = []

        self.logger.info("AutoReplyService activated")
        self.status_changed.emit("active", "🤖 Auto Mode: Active")

        # 1. Announce entry into automated mode
        greeting = (
            self.settings.auto_reply_greeting
            or "This call is now set to automated AI mode."
        )
        if greeting and self._tts_callback:
            self.logger.info(f"Speaking greeting announcement: '{greeting}'")
            self._tts_callback(greeting)

        # 2. Start audio listening thread
        self._listener_thread = threading.Thread(
            target=self._audio_listener_worker,
            daemon=True,
            name="AutoReplyListener",
        )
        self._listener_thread.start()

    def stop(self) -> None:
        """Stop auto-reply mode."""
        if not self.is_active:
            return

        self.is_active = False
        self._stop_event.set()

        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=1.5)
        self._listener_thread = None

        self.logger.info("AutoReplyService deactivated")
        self.status_changed.emit("stopped", "Auto Mode: Off")

    def _audio_listener_worker(self) -> None:
        """
        Background worker that continuously captures audio, runs VAD,
        and triggers Whisper transcription and LLM responses on silence.
        """
        if not PYAUDIO_AVAILABLE:
            self.logger.error("PyAudio not available for AutoReply listener")
            self.status_changed.emit("error", "PyAudio missing")
            return

        pa = pyaudio.PyAudio()
        sample_rate = 16000
        chunk_size = 1024
        channels = 1

        # Use configured mic if set
        device_index = None
        if self.settings.mic_input_device_id is not None:
            try:
                device_index = int(self.settings.mic_input_device_id)
            except (ValueError, TypeError):
                device_index = None

        try:
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=chunk_size,
            )
        except Exception as e:
            self.logger.error(f"Failed to open audio input stream: {e}")
            self.status_changed.emit("error", "Mic open failed")
            pa.terminate()
            return

        self.logger.info("AutoReply audio capture stream opened successfully")
        self.status_changed.emit("listening", "🤖 Auto Mode: Listening...")

        recording = False
        recorded_frames: List[bytes] = []
        silence_start_time: Optional[float] = None
        speech_start_time: Optional[float] = None

        energy_threshold = self.settings.auto_reply_energy_threshold or 0.02
        silence_duration_needed = self.settings.auto_reply_silence_duration or 1.5

        try:
            while not self._stop_event.is_set():
                # If TTS is speaking, discard incoming audio to avoid echo
                if self.is_speaking:
                    recording = False
                    recorded_frames.clear()
                    silence_start_time = None
                    speech_start_time = None
                    try:
                        stream.read(chunk_size, exception_on_overflow=False)
                    except Exception:
                        pass
                    time.sleep(0.05)
                    continue

                try:
                    data = stream.read(chunk_size, exception_on_overflow=False)
                except Exception:
                    time.sleep(0.02)
                    continue

                if not data:
                    continue

                # Compute RMS energy level
                audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                rms = float(np.sqrt(np.mean(np.square(audio_np))))

                now = time.time()
                is_speech = rms >= energy_threshold

                if is_speech:
                    if not recording:
                        recording = True
                        recorded_frames = []
                        speech_start_time = now
                        self.status_changed.emit("hearing", "🤖 Auto Mode: Hearing speech...")
                        self.logger.debug(f"Speech detected (RMS: {rms:.4f})")

                    recorded_frames.append(data)
                    silence_start_time = None
                else:
                    if recording:
                        recorded_frames.append(data)
                        if silence_start_time is None:
                            silence_start_time = now
                        elif now - silence_start_time >= silence_duration_needed:
                            # Caller finished speaking!
                            recording = False
                            total_duration = now - (speech_start_time or now)
                            silence_start_time = None

                            if total_duration >= 0.6 and len(recorded_frames) > 5:
                                # Process speech buffer
                                audio_bytes = b"".join(recorded_frames)
                                self._handle_recorded_utterance(audio_bytes, sample_rate)
                            else:
                                self.logger.debug("Speech snippet too short; discarded")
                                self.status_changed.emit("listening", "🤖 Auto Mode: Listening...")

                            recorded_frames = []

        except Exception as e:
            self.logger.error(f"Error in audio listener loop: {e}", exc_info=True)
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            pa.terminate()
            self.logger.info("AutoReply audio capture stream terminated")

    def _handle_recorded_utterance(self, audio_data: bytes, sample_rate: int) -> None:
        """Process recorded caller speech: transcribe and trigger AI response."""
        self.status_changed.emit("thinking", "🤖 Auto Mode: Transcribing...")

        # Save to temp WAV file
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_wav_path = temp_wav.name
        temp_wav.close()

        try:
            with wave.open(temp_wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data)

            # Transcribe with Whisper
            text = self._transcribe_wav(temp_wav_path)
            if not text or len(text.strip()) < 2:
                self.logger.debug("Empty or noise transcription, skipping AI reply")
                self.status_changed.emit("listening", "🤖 Auto Mode: Listening...")
                return

            # Clean hallucinated artifacts
            cleaned_text = text.strip()
            self.logger.info(f"Transcribed caller speech: '{cleaned_text}'")
            self.transcription_ready.emit(cleaned_text)

            # Generate AI response
            self.status_changed.emit("thinking", "🤖 Auto Mode: Thinking...")
            ai_reply = self._query_llm_api(cleaned_text)

            if ai_reply and self._tts_callback:
                self.logger.info(f"AI Auto-Reply Response: '{ai_reply}'")
                self.ai_response_ready.emit(ai_reply)
                self.status_changed.emit("speaking", "🤖 Auto Mode: Speaking...")
                self._tts_callback(ai_reply)
            else:
                self.status_changed.emit("listening", "🤖 Auto Mode: Listening...")

        except Exception as e:
            self.logger.error(f"Error processing recorded utterance: {e}", exc_info=True)
            self.status_changed.emit("listening", "🤖 Auto Mode: Listening...")
        finally:
            try:
                if os.path.exists(temp_wav_path):
                    os.unlink(temp_wav_path)
            except Exception:
                pass

    def _transcribe_wav(self, wav_path: str) -> str:
        """Transcribe audio file using Whisper."""
        try:
            import whisper

            if self._whisper_model is None:
                self.logger.info("Loading Whisper base model for live transcription...")
                self._whisper_model = whisper.load_model("base")

            result = self._whisper_model.transcribe(wav_path, fp16=False)
            return result.get("text", "").strip()
        except Exception as e:
            self.logger.error(f"Whisper transcription failed: {e}")
            return ""

    def _query_llm_api(self, user_prompt: str) -> Optional[str]:
        """
        Send user prompt and context to the configured LLM API
        (LiteLLM, OpenAI, Gemini, OpenCode, Ollama).
        """
        api_url = (self.settings.auto_reply_api_url or "http://localhost:4000/v1").rstrip("/")
        if not api_url.endswith("/chat/completions"):
            endpoint = f"{api_url}/chat/completions"
        else:
            endpoint = api_url

        model = self.settings.auto_reply_model or "gemini-3.5-flash"
        api_key = self.settings.auto_reply_api_key or "sk-aira-master-key"
        system_prompt = (
            self.settings.auto_reply_system_prompt
            or "You are an AI assistant in a live voice call. Respond naturally, conversationally, concisely (1-2 sentences), and directly to what was said."
        )

        # Build message history
        messages = [{"role": "system", "content": system_prompt}]
        for turn in self.conversation_history[-6:]:
            messages.append(turn)
        messages.append({"role": "user", "content": user_prompt})

        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 120,
        }

        self.logger.debug(f"Querying LLM at {endpoint} with model {model}...")

        try:
            if not REQUESTS_AVAILABLE:
                # Fallback to standard library urllib
                import urllib.request
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=12) as response:
                    data = json.loads(response.read().decode("utf-8"))
            else:
                resp = requests.post(endpoint, json=payload, headers=headers, timeout=12)
                resp.raise_for_status()
                data = resp.json()

            reply = data["choices"][0]["message"]["content"].strip()

            # Record turn in conversation history
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "assistant", "content": reply})

            return reply

        except Exception as e:
            self.logger.error(f"LLM API query failed ({endpoint}): {e}")
            # Intelligent conversational fallback
            return "Sorry, I had a brief connection glitch. Could you say that one more time?"
