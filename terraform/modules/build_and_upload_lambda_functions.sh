#!/bin/bash
set -euo pipefail

# --------------------------------------------------------------------------------------------
# This script builds and uploads a Lambda functions to AWS.
# Script: build_and_upload_lambda_functions.sh
# Purpose: Build, package, and upload all (ot targeted) AWS Lambda function(s) as deterministic
#          zip files to AWS S3 for terraform deployment.
# Usage: ./build_and_upload_lambda_functions.sh [ENV]
#          ENV: The environment to deploy to (e.g., dev, prod) (default: dev).
# Env:     ONLY_USECASE (optional): If set, only built and upload specific usecase.
# --------------------------------------------------------------------------------------------

# Print Usage and exit
if [[ ${1:-} == "--help" || ${1:-} == "-h" ]]; then
  echo "Usage: $0 [ENV]"
  echo "  ENV: The environment to deploy to (e.g., dev, prod). Default is dev"
  echo "  ONLY_USECASE (optional): If set, only built and upload specific usecase"
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

echo "[INFO] Building and uploading Lambda functions..."
# Python build settings
PYTHON_VERSION="3.13"
PIP_PARAMS="--platform manylinux2014_x86_64 --implementation cp --python $PYTHON_VERSION --only-binary=:all: --compile --upgrade"

echo "[INFO] Building and uploading Lambda functions for environment: $ENV"
# Discover all usecases
if [ -n "${ONLY_USECASE:-}" ]; then
  USECASES=("$ONLY_USECASE")
else
  USECASES=()
  for FUNC_PATH in "$REPO_ROOT_DIR/src/functions/"*; do
    [ -d "$FUNC_PATH" ] || continue
    USECASES+=("$(basename "$FUNC_PATH")")
  done          
fi

for USECASE_NAME in "${USECASES[@]}"; do
  FUNC_PATH="$REPO_ROOT_DIR/src/functions/$USECASE_NAME"
  DEPLOY_DIR="$REPO_ROOT_DIR/build/functions/$USECASE_NAME"
  rm -rf "$DEPLOY_DIR"
  mkdir -p "$DEPLOY_DIR"

  # Validate source directory
  for DIR in "$FUNC_PATH"; do
    if [ ! -d "$DIR" ]; then
      echo "[WARN] Source directory '$DIR' does not exist or is empty. Skipping usecase '$USECASE_NAME'."
      continue 2
    fi
  done

  cp -r "$FUNC_PATH/." "$DEPLOY_DIR/src"

  # Create deterministic zip: fix timestamps, sort files, omit extra attrs, exclude unwanted
  (cd "$DEPLOY_DIR" && \
    find src -type f \
     ! -name '*.pyc' \
     ! -name '*.pyo' \
     ! -name '*.so' \
     ! -name '*.DS_Store' \
     ! -name '*.egg-info' \
     ! -name '*.log' \
     ! -name '__pycache__' \
     ! -path '*/__pycache__/*' \
     -print0 | xargs -0r touch -t 202201010000)

  (cd "$DEPLOY_DIR" && \
    find src -type f \
     ! -name '*.pyc' \
     ! -name '*.pyo' \
     ! -name '*.so' \
     ! -name '*.DS_Store' \
     ! -name '*.egg-info' \
     ! -name '*.log' \
     ! -name '__pycache__' \
     ! -path '*/__pycache__/*' \
     | LC_ALL=C sort | zip -X -D -@ "../${USECASE_NAME}.zip")

  ZIP_PATH="$REPO_ROOT_DIR/build/functions/${USECASE_NAME}.zip"
  openssl dgst -sha256 "$ZIP_PATH" | openssl enc -d -A -base64 > "$ZIP_PATH.sha256"
  aws s3 cp "$ZIP_PATH" "s3://$CODE_STORE_BUCKET/${USECASE_NAME}_lambda_package/${USECASE_NAME}.zip"
  aws s3 cp "$ZIP_PATH.sha256" "s3://$CODE_STORE_BUCKET/${USECASE_NAME}_lambda_package/${USECASE_NAME}.zip.sha256" --content-type "text/plain"
  rm "$ZIP_PATH.sha256"
  echo "[INFO] Uploaded Lambda function '$USECASE_NAME' to s3"
done

echo "[INFO] All Lambda functions zips built and uploaded to s3 for env: $ENV, bucket: $CODE_STORE_BUCKET"