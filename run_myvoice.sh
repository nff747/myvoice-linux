#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
export HF_HUB_DISABLE_XET=1
export PYTHONPATH="$SCRIPT_DIR/src"
export QT_QPA_PLATFORM=xcb
exec .venv/bin/python -m myvoice.main "$@"