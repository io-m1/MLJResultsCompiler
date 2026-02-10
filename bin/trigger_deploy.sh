#!/usr/bin/env bash
# Trigger Render Deployment using Deploy Hook

if [ -z "$RENDER_DEPLOY_HOOK" ]; then
    echo "Error: RENDER_DEPLOY_HOOK environment variable is not set."
    echo "Please set it or provide it as a GitHub Secret."
    exit 1
fi

echo "Triggering Render deployment..."
curl -X POST "$RENDER_DEPLOY_HOOK"
echo -e "\n✓ Deployment triggered successfully"
