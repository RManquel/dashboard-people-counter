#!/usr/bin/env bash
# Build and tag Docker images for ECR
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration — override via env vars
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-123456789012}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO_BACKEND="${ECR_REPO_BACKEND:-stadium-backend}"
ECR_REPO_FRONTEND="${ECR_REPO_FRONTEND:-stadium-frontend}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

ECR_BASE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "📦 Building images..."
cd "$PROJECT_ROOT"

docker build -t "${ECR_REPO_BACKEND}:${IMAGE_TAG}" ./backend
docker build -t "${ECR_REPO_FRONTEND}:${IMAGE_TAG}" ./frontend

docker tag "${ECR_REPO_BACKEND}:${IMAGE_TAG}" "${ECR_BASE}/${ECR_REPO_BACKEND}:${IMAGE_TAG}"
docker tag "${ECR_REPO_FRONTEND}:${IMAGE_TAG}" "${ECR_BASE}/${ECR_REPO_FRONTEND}:${IMAGE_TAG}"

echo "✅ Images built and tagged for ECR: ${ECR_BASE}"
