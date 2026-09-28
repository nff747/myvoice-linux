"""
Kokoro Neural TTS Engine

Provides ultra-fast (sub-300ms) and ultra-realistic voice synthesis
using Kokoro-82M ONNX runtime.
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Optional, Dict, Tuple, List, AsyncIterator
import numpy as np

logger = logging.getLogger(__name__)

# Default model directory
DEFAULT_KOKORO_DIR = Path.home() / ".cache" / "kokoro"
DEFAULT_MODEL_FILE = DEFAULT_KOKORO_DIR / "kokoro-v1.0.onnx"
DEFAULT_VOICES_FILE = DEFAULT_KOKORO_DIR / "voices-v1.0.bin"

# Mapping from friendly speaker names to Kokoro voice IDs
VOICE_MAP: Dict[str, str] = {
    "Heart": "af_heart",       # Ultra-natural warm female (primary)
    "Adam": "am_adam",         # Deep articulate male
    "Bella": "af_bella",       # Bright cheerful female
    "Sarah": "af_sarah",       # Calm professional female
    "Michael": "am_michael",   # Friendly relaxed male
    "Emma": "bf_emma",         # Elegant British female
    "George": "bm_george",     # Polished British male
    "Ryan": "am_adam",         # Mapped from legacy Ryan
    "Aiden": "am_michael",     # Mapped from legacy Aiden
    "Vivian": "af_heart",      # Mapped from legacy Vivian
    "Serena": "af_bella",      # Mapped from legacy Serena
    "Uncle_Fu": "bm_george",   # Mapped from legacy Uncle_Fu
    "Dylan": "am_adam",        # Mapped from legacy Dylan
    "Eric": "am_michael",      # Mapped from legacy Eric
    "Ono_Anna": "jf_alpha",    # Mapped from legacy Ono_Anna
    "Sohee": "af_heart",       # Mapped from legacy Sohee
}


class KokoroEngine:
    """
    Ultra-fast neural TTS engine powered by Kokoro ONNX.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        voices_path: Optional[Path] = None,
        num_threads: int = 8,
    ):
        self.model_path = Path(model_path or DEFAULT_MODEL_FILE)
        self.voices_path = Path(voices_path or DEFAULT_VOICES_FILE)
        self.num_threads = num_threads
        self._kokoro = None
        self._lock = asyncio.Lock()
        self._is_initialized = False

    def is_available(self) -> bool:
        """Check if model and voice files exist on disk."""
        return self.model_path.exists() and self.voices_path.exists()

    def _ensure_loaded_sync(self):
        """Synchronously load the Kokoro ONNX model and voices session."""
        if self._is_initialized and self._kokoro is not None:
            return

        if not self.is_available():
            raise FileNotFoundError(
                f"Kokoro model files not found at {self.model_path} or {self.voices_path}"
            )

        import onnxruntime as ort
        from kokoro_onnx import Kokoro

        t0 = time.perf_counter()
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = self.num_threads
        opts.inter_op_num_threads = 2
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        session = ort.InferenceSession(
            str(self.model_path),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        self._kokoro = Kokoro.from_session(session, str(self.voices_path))
        self._is_initialized = True
        logger.info(
            f"KokoroEngine initialized in {(time.perf_counter() - t0) * 1000:.1f}ms "
            f"using {self.num_threads} CPU threads."
        )

    def get_voice_id(self, speaker_name: str) -> str:
        """Resolve a speaker name to a valid Kokoro voice ID."""
        if speaker_name in VOICE_MAP:
            return VOICE_MAP[speaker_name]
        # Check if already a raw voice ID
        if speaker_name.startswith("af_") or speaker_name.startswith("am_") or \
           speaker_name.startswith("bf_") or speaker_name.startswith("bm_") or \
           speaker_name.startswith("jf_") or speaker_name.startswith("zf_"):
            return speaker_name
        return "af_heart"

    def synthesize_sync(
        self,
        text: str,
        speaker: str = "Heart",
        speed: float = 1.0,
        lang: str = "en-us",
    ) -> Tuple[np.ndarray, int]:
        """
        Synchronously synthesize text to audio samples and sample rate (24000Hz).
        """
        self._ensure_loaded_sync()
        voice_id = self.get_voice_id(speaker)
        t0 = time.perf_counter()
        samples, sample_rate = self._kokoro.create(
            text=text,
            voice=voice_id,
            speed=speed,
            lang=lang,
        )
        duration_sec = len(samples) / sample_rate
        latency_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            f"Kokoro synthesized {len(text)} chars ({duration_sec:.2f}s audio) "
            f"in {latency_ms:.1f}ms [Voice: {speaker}->{voice_id}]"
        )
        return samples, sample_rate

    async def synthesize(
        self,
        text: str,
        speaker: str = "Heart",
        speed: float = 1.0,
        lang: str = "en-us",
    ) -> Tuple[np.ndarray, int]:
        """
        Asynchronously synthesize text to audio using thread pool.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self.synthesize_sync, text, speaker, speed, lang
        )

    async def synthesize_stream(
        self,
        text: str,
        speaker: str = "Heart",
        speed: float = 1.0,
        lang: str = "en-us",
    ) -> AsyncIterator[Tuple[np.ndarray, int]]:
        """
        Asynchronously stream chunks of generated audio.
        """
        self._ensure_loaded_sync()
        voice_id = self.get_voice_id(speaker)
        async for chunk, sample_rate in self._kokoro.create_stream(
            text=text,
            voice=voice_id,
            speed=speed,
            lang=lang,
        ):
            yield chunk, sample_rate
