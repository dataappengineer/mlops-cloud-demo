#!/bin/bash
set -e

echo "🗑️  MLOps Cloud Teardown Script"
echo "================================"

cd terraform

echo "⚠️  WARNING: This will destroy ALL infrastructure!"
echo ""
terraform show
echo ""

read -p "Are you sure you want to destroy everything? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Teardown cancelled"
    exit 0
fi

echo "🗑️  Destroying infrastructure..."
terraform destroy

echo "✅ All resources destroyed"
echo ""
echo "💡 Remember to:"
echo "  1. Check AWS Console for any remaining resources"
echo "  2. Verify ECR images are deleted"
echo "  3. Check CloudWatch logs retention"
