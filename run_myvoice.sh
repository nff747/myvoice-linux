#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Automatically configure PipeWire / PulseAudio Virtual Routing for Discord & Voice Chat
if command -v pactl &> /dev/null; then
    DEFAULT_SINK=$(pactl get-default-sink 2>/dev/null)
    DEFAULT_SOURCE=$(pactl get-default-source 2>/dev/null)

    # 1. Create Virtual Mic Sink
    if ! pactl list modules short 2>/dev/null | grep -q "myvoice_virtual_mic"; then
        pactl load-module module-null-sink sink_name=myvoice_virtual_mic sink_properties=device.description="MyVoice_Virtual_Mic" >/dev/null 2>&1
    fi

    # 2. Remap to virtual input source for Discord
    if ! pactl list sources short 2>/dev/null | grep -q "myvoice_mic"; then
        pactl load-module module-remap-source master=myvoice_virtual_mic.monitor source_name=myvoice_mic source_properties=device.description="MyVoice_Virtual_Microphone" >/dev/null 2>&1
    fi

    # 3. Create Combined Sink so audio plays to BOTH your headphones AND Discord
    if [ -n "$DEFAULT_SINK" ] && [ "$DEFAULT_SINK" != "myvoice_combined_sink" ]; then
        if ! pactl list modules short 2>/dev/null | grep -q "myvoice_combined_sink"; then
            pactl load-module module-combine-sink sink_name=myvoice_combined_sink slaves="$DEFAULT_SINK",myvoice_virtual_mic sink_properties=device.description="MyVoice_Combined" >/dev/null 2>&1
        fi
        pactl set-default-sink myvoice_combined_sink >/dev/null 2>&1
    fi

    # 4. Loop real microphone into virtual mic (so your voice and AI voice both work together)
    if [ -n "$DEFAULT_SOURCE" ] && [ "$DEFAULT_SOURCE" != "myvoice_mic" ]; then
        if ! pactl list modules short 2>/dev/null | grep -q "module-loopback.*myvoice_virtual_mic"; then
            pactl load-module module-loopback source="$DEFAULT_SOURCE" sink=myvoice_virtual_mic latency_msec=20 >/dev/null 2>&1
        fi
    fi
fi

export HF_HUB_DISABLE_XET=1
export PYTHONPATH="$SCRIPT_DIR/src"
export QT_QPA_PLATFORM=xcb
exec .venv/bin/python -m myvoice.main "$@"