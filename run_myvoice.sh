#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Clean PipeWire / PulseAudio Virtual Audio Setup
if command -v pactl &> /dev/null; then
    if ! pactl list modules short 2>/dev/null | grep -q "myvoice_virtual_mic"; then
        pactl load-module module-null-sink sink_name=myvoice_virtual_mic sink_properties=device.description="MyVoice_Virtual_Mic" >/dev/null 2>&1
    fi
    if ! pactl list sources short 2>/dev/null | grep -q "myvoice_mic"; then
        pactl load-module module-remap-source master=myvoice_virtual_mic.monitor source_name=myvoice_mic source_properties=device.description="MyVoice_Virtual_Microphone" >/dev/null 2>&1
    fi
fi

export HF_HUB_DISABLE_XET=1
export PYTHONPATH="$SCRIPT_DIR/src"
export QT_QPA_PLATFORM=xcb
exec .venv/bin/python -m myvoice.main "$@"