#!/usr/bin/env bash
#
# Generates ArgoCD Application manifests from:
# - argocd-example-apps-official
# - argocd-example-apps-local
#
# Application manifests generated are placed in ./build
#
# Usage:
#   ./generate.sh
#

set -e -o pipefail

mkdir -p build
helm template argocd-example-apps ./argocd-example-apps-official/apps >build/argocd-example-apps-official.yaml
