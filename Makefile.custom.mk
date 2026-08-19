SHELL:=/usr/bin/env bash

##@ Generate

.PHONY: generate
generate: ## Replace variables on Helm manifests.
	./hack/template.sh

.PHONY: verify
verify:
	@$(MAKE) generate
	git diff --exit-code

##@ Test

.PHONY: clean
clean: ## Delete test manifests from kind cluster.
	./hack/cleanup-local.sh

.PHONY: dabs
dabs: generate
	dabs.sh --generate-metadata --chart-dir helm/kyverno-policies-dx
	
##@ Test (ValidatingPolicies)

# Owned here rather than in Makefile.gen.chainsaw.mk because it is specific to this
# repository: only kyverno-policies-dx has a tests/cel/ suite. devctl dropped the target
# from the shared chainsaw template, which broke the hand-written
# .github/workflows/test-kyverno-vpol-policies-with-chainsaw.yaml that calls it. Keeping
# it in this file, which align-files does not regenerate, makes it survive.
.PHONY: install-cel-policies
install-cel-policies: ## Install the chart with the ValidatingPolicy (CEL) test values.
	touch tests/cel/chainsaw/values.yaml
	helm upgrade --install $(KYVERNO_POLICIES_APP_NAME) ./helm/$(KYVERNO_POLICIES_APP_NAME) --values ./tests/cel/chainsaw/values.yaml
