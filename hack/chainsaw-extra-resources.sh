#!/usr/bin/env bash

set -euo pipefail

# Pre-install CRDs before policies so that:
# 1. Kyverno admission webhooks are registered for these resource types at policy install time.
# 2. Helm .Capabilities.APIVersions checks succeed for conditional policies.

echo "Installing App CRD (application.giantswarm.io)..."
kubectl apply -f https://raw.githubusercontent.com/giantswarm/apiextensions-application/main/config/crd/application.giantswarm.io_apps.yaml

echo "Installing KEDA CRDs (includes ScaledObject)..."
kubectl apply --server-side -f https://github.com/kedacore/keda/releases/download/v2.19.0/keda-2.19.0-crds.yaml

echo "Installing SecretStore CRD (external-secrets.io)..."
kubectl apply --server-side -f https://raw.githubusercontent.com/external-secrets/external-secrets/v0.10.7/config/crds/bases/external-secrets.io_secretstores.yaml

echo "Installing ClusterSecretStore CRD (external-secrets.io)..."
kubectl apply --server-side -f https://raw.githubusercontent.com/external-secrets/external-secrets/v0.10.7/config/crds/bases/external-secrets.io_clustersecretstores.yaml

echo "Installing Provider CRD (pkg.crossplane.io)..."
kubectl apply -f https://raw.githubusercontent.com/crossplane/crossplane/v2.2.0/cluster/crds/pkg.crossplane.io_providers.yaml

echo "All extra resources installed."
