"""
Unit tests for KokoroEngine.
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch

from myvoice.services.kokoro_engine import KokoroEngine, VOICE_MAP


def test_kokoro_engine_init_defaults():
    engine = KokoroEngine()
    assert engine.num_threads == 8
    assert engine.get_voice_id("Heart") == "af_heart"
    assert engine.get_voice_id("Adam") == "am_adam"
    assert engine.get_voice_id("Ryan") == "am_adam"
    assert engine.get_voice_id("unknown_voice") == "af_heart"


def test_kokoro_engine_voice_mapping():
    engine = KokoroEngine()
    for name, voice_id in VOICE_MAP.items():
        assert engine.get_voice_id(name) == voice_id
    assert engine.get_voice_id("af_bella") == "af_bella"


def test_kokoro_engine_availability():
    engine = KokoroEngine()
    # If the model is downloaded on the dev environment, is_available is True
    cache_model = Path.home() / ".cache" / "kokoro" / "kokoro-v1.0.onnx"
    if cache_model.exists():
        assert engine.is_available() is True
    else:
        # Non-existent path returns False
        fake_engine = KokoroEngine(model_path=Path("/fake/nonexistent.onnx"))
        assert fake_engine.is_available() is False


@pytest.mark.asyncio
async def test_kokoro_engine_synthesis_if_available():
    engine = KokoroEngine()
    if not engine.is_available():
        pytest.skip("Kokoro model not downloaded on this machine")

    samples, sr = await engine.synthesize("Hello world!", speaker="Heart")
    assert isinstance(samples, np.ndarray)
    assert sr == 24000
    assert len(samples) > 0
    assert samples.dtype == np.float32 or samples.dtype == np.float64
