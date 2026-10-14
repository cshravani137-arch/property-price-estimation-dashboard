#!/bin/bash
# Launch PropertyLens on macOS. Double-click this file after extracting the project.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install it from https://www.python.org/downloads/macos/ and try again."
  read -r -p "Press Enter to close this window..." _
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Setting up a private Python environment..."
  python3 -m venv .venv || exit 1
fi

source .venv/bin/activate
if ! python -c "import streamlit, pandas, sklearn, plotly" >/dev/null 2>&1; then
  echo "Installing dashboard packages. Internet access is required on the first run..."
  python -m pip install --upgrade pip || exit 1
  python -m pip install -r requirements.txt || exit 1
fi

echo "Starting PropertyLens. Keep this window open while using the dashboard."
python -m streamlit run app.py
