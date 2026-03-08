#!/usr/bin/env bash
# Push images to ECR and trigger ECS deploy
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-123456789012}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO_BACKEND="${ECR_REPO_BACKEND:-stadium-backend}"
ECR_REPO_FRONTEND="${ECR_REPO_FRONTEND:-stadium-frontend}"
ECS_CLUSTER="${ECS_CLUSTER:-stadium-cluster}"
ECS_SERVICE="${ECS_SERVICE:-stadium-service}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

ECR_BASE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "🔐 Authenticating with ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ECR_BASE"

echo "📤 Pushing images..."
docker push "${ECR_BASE}/${ECR_REPO_BACKEND}:${IMAGE_TAG}"
docker push "${ECR_BASE}/${ECR_REPO_FRONTEND}:${IMAGE_TAG}"

echo "🚀 Triggering ECS rolling deploy..."
aws ecs update-service \
  --cluster "$ECS_CLUSTER" \
  --service "$ECS_SERVICE" \
  --force-new-deployment \
  --region "$AWS_REGION"

echo "✅ Deploy triggered. Monitor at:"
echo "   https://${AWS_REGION}.console.aws.amazon.com/ecs/v2/clusters/${ECS_CLUSTER}/services/${ECS_SERVICE}/deployments"
