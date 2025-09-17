#!/bin/bash
set -euo pipefail

# --------------------------------------------------------------------------------------------
# This script builds and uploads a Lambda layer to AWS.
# Script: build_and_upload_lambda_layer.sh
# Purpose: Build, package, and upload a Lambda layers as deterministic
#          zip files to AWS S3 for terraform deployment.
# Usage: ./build_and_upload_lambda_layer.sh [ENV]
#          ENV: The environment to deploy to (e.g., dev, prod).
# Env:     ONLY_LAYER_NAME (optional): If set, only this layer will be built and uploaded.
# --------------------------------------------------------------------------------------------

# Print Usage and exit
if [[ ${1:-} == "--help" || ${1:-} == "-h" ]]; then
  echo "Usage: $0 [ENV]"
  echo "  ENV: The environment to deploy to (e.g., dev, prod). Default is dev"
  echo "  ONLY_LAYER_NAME (optional): If set, only this layer will be built and uploaded."
  exit 0
fi

# Set environment
if [ $# -ge 1 ]; then
  ENV="$1"
elif [ -z "${ENV:-}" ]; then
  ENV="dev"
fi

# Find repo root directory
REPO_ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# Load environment config
CONFIG_FILE="$REPO_ROOT_DIR/terraform/config/terraform_config.tfvars"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Config file '$CONFIG_FILE' not found!" >&2
  exit 1
fi

# Extract S3 bucket name
CODE_STORE_BUCKET=$(awk -F'"' '/^code_store_bucket/{print $2}' "$CONFIG_FILE")
if [ -z "$CODE_STORE_BUCKET" ]; then
  echo "Error: 'code_store_bucket' not found in config file!" >&2
  exit 1
fi

# Python build settings
PYTHON_VERSION="3.13"
PIP_PARAMS="--platform manylinux2014_x86_64 --implementation cp --only-binary=:all: --compile --upgrade"

echo "[INFO] Building and uploading Lambda layers to S3 bucket: $CODE_STORE_BUCKET for environment: $ENV"

# Only build the packages layer
LAYERS=(packages)

for LAYER in "${LAYERS[@]}"; do
  SRC_DIR="$REPO_ROOT_DIR/src/layers/$LAYER"
  if [ ! -d "$SRC_DIR" ] || [ -z "$(ls -A "$SRC_DIR")" ]; then
    echo "[WARN] Source directory '$SRC_DIR' does not exist or is empty. Skipping layer '$LAYER'."
    continue
  fi

  LAYER_BUILD_DIR="$REPO_ROOT_DIR/build/layers/$LAYER"
  rm -rf "$LAYER_BUILD_DIR"
  mkdir -p "$LAYER_BUILD_DIR/python"

  # Only build packages layer
  # Build Python packages layer: Only core requirements.txt
  python3 -m venv "$LAYER_BUILD_DIR/venv"
  cp "$SRC_DIR/requirements.txt" "$LAYER_BUILD_DIR/venv/requirements.txt"
  source "$LAYER_BUILD_DIR/venv/bin/activate"
  echo "[DEBUG] Python version: $(python --version)"
  echo "[DEBUG] Pip version: $(pip --version)"
  pip install --upgrade pip

  rm -rf "$LAYER_BUILD_DIR/python"/*
  echo "[DEBUG] Installing requirement.txt to $LAYER_BUILD_DIR/python"
  if ! pip install $PIP_PARAMS -r "$LAYER_BUILD_DIR/venv/requirements.txt" -t "$LAYER_BUILD_DIR/python"; then
    echo "[ERROR] One or more dependencies failed to installed as wheels. Lambda layers only contains wheels. Aborting."
    deactivate
    rm -rf "$LAYER_BUILD_DIR"
    exit 1
  fi
  echo "[INFO] Installed files in python/:"
  find "$LAYER_BUILD_DIR/python" | sort 
  deactivate
  rm -rf "$LAYER_BUILD_DIR/venv"
  SRC_FILES=$(find "$LAYER_BUILD_DIR/python" -mindepth 3 -maxdepth 2 -name 'setup.py' -print0 | xargs -0r dirname)
  if [ -n "$SRC_FILES" ]; then
    echo "[ERROR] Source trees detected in layer:"
    echo "$SRC_FILES"
    exit 1
  fi

  find "$LAYER_BUILD_DIR/python" -type d -name '__pycache__' -exec rm -rf {} +

  find "$LAYER_BUILD_DIR/python" -type f -print0 | xargs -0 touch -t 202401010000

  # Create deterministic zip
  (cd "$LAYER_BUILD_DIR" && find python -type f | LC_ALL=C sort | zip -X -D -@ "../${LAYER}.zip")
  ZIP_PATH="$REPO_ROOT_DIR/build/layers/${LAYER}.zip"
  echo "[DEBUF] Contents of $ZIP_PATH:"
  unzip -l "$ZIP_PATH"

  openssl dgst -sha256 --binary "$ZIP_PATH" | openssl enc -base64 > "$ZIP_PATH.sha256"
  echo "[DEBUG] SHA256 hash: $(cat "$ZIP_PATH.sha256")"

  # Upload to S3
  S3_KEY="lambda_layers/$(basename "$ZIP_PATH")"
  S3_HASH_KEY="lambda_layers/$(basename "$ZIP_PATH.sha256")"
  aws s3 cp "$ZIP_PATH" "s3://$CODE_STORE_BUCKET/$S3_KEY" --no-progress --only-show-errors
  aws s3 cp "$ZIP_PATH.sha256" "s3://$CODE_STORE_BUCKET/$S3_HASH_KEY" --content-type "text/plain" --no-progress --only-show-errors
  echo "[DEBUG] s3 ETag for $S3_KEY: $(aws s3api head-object --bucket "$CODE_STORE_BUCKET" --key "$S3_KEY" --query ETag)"
  echo "[DEBUG] s3 ETag for $S3_HASH_KEY: $(aws s3api head-object --bucket "$CODE_STORE_BUCKET" --key "$S3_HASH_KEY" --query ETag)"
  rm "$ZIP_PATH.sha256"
  echo "[INFO] Uploaded $(basename "$ZIP_PATH") and its SHA256 hash to s3"
done

echo "[INFO] All Lambda layers zips built and uploaded to s3 for env: $ENV, bucket: $CODE_STORE_BUCKET"