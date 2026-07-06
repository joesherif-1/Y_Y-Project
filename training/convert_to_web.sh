#!/usr/bin/env bash
# Converts the Colab-trained model (skin_model.zip) into the TensorFlow.js files
# the website loads from static/model/.
#
# Run on a computer with Python 3.10+ installed:
#   ./training/convert_to_web.sh path/to/skin_model.zip
set -euo pipefail

ZIP="${1:?Usage: ./training/convert_to_web.sh path/to/skin_model.zip}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

unzip -q "$ZIP" -d "$WORK/savedmodel"

echo "Setting up the converter (one-time, ~2 min)..."
python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" -q install --upgrade pip
# tensorflow-decision-forests is only needed for tree models; skip it if unavailable.
"$WORK/venv/bin/pip" -q install tensorflowjs || \
    "$WORK/venv/bin/pip" -q install tensorflowjs --no-deps tensorflow tf-keras tensorflow-hub packaging six
# Fix a protobuf version clash between the converter's own dependencies.
"$WORK/venv/bin/pip" -q install -U "protobuf>=6.31"

echo "Converting..."
mkdir -p "$REPO_DIR/static/model"
"$WORK/venv/bin/tensorflowjs_converter" \
    --input_format=tf_saved_model \
    --output_format=tfjs_graph_model \
    "$WORK/savedmodel" "$REPO_DIR/static/model"

[ -f "$WORK/savedmodel/metrics.json" ] && cp "$WORK/savedmodel/metrics.json" "$REPO_DIR/static/model/"

echo "Done! Files written to static/model/ — commit and push them:"
echo "  git add static/model && git commit -m 'Add trained skin-check model' && git push"
