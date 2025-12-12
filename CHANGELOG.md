# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.3] - 2025-12-12

### Changed

- Migrate Chart.yaml annotations to new format as per https://docs.giantswarm.io/reference/platform-api/chart-metadata/

## [0.8.2] - 2025-12-12

### Changed

- Migrate build system to ABS.

## [0.8.1] - 2025-11-26

### Changed

- Removed `restart-dex-on-secrets-change` policy.

### Fixed

- Missing RBAC for kyverno-report-controller

## [0.8.0] - 2025-08-25

### Added

- Add `enforce-fallback-config-scaledobjects` ClusterPolicy.

## [0.7.2] - 2025-08-20

### Changed

- Fixed restart-dex-on-secrets-change ClusteRole annotations

## [0.7.1] - 2025-08-19

### Added

- ClusteRole and ClusterPolicy for dex to restart on secret configuration changes

## [0.7.0] - 2025-06-05

### Added

- Cluster roles required by changes to kyverno: issue-33418

### Changed

- Update tests to newer runners.

## [0.6.0] - 2025-02-19

### Changed

- Use `Enforce` instead of `enforce` validationFailureAction.

## [0.5.1] - 2024-09-25

### Changed

- Use `Enforce` and `Audit` validationFailureAction.

## [0.5.0] - 2024-03-22

### Added

- Add policy to block `k8s-initiator-app` deployment on CAPA.

## [0.4.5] - 2024-03-18

### Removed

- Removed `check-deprecated-apis-1-22/25` policies since the CRDs are not present anymore.

## [0.4.4] - 2024-02-13

### Removed

- Remove `KustomizeController` PolicyException.

## [0.4.3] - 2024-02-13

### Added

- Push to `vsphere` app collection.
- Don't push to `openstack` app collection.
- Add policy exception for `kustomize-controller` in `flux-giantswarm` Namespace.
- Added the new registry `gsoci.azurecr.io/giantswarm/*` and `gsociprivate.azurecr.io/giantswarm/*`to kyverno-policy enforcing registries.

## [0.4.2] - 2023-02-09

### Changed

- Added back the previous `Aliyun` registry to avoid false positives on images that have not been migrated to the new one yet.

### Added

- Push to `capz` app collection.

## [0.4.1] - 2023-02-07

### Changed

- Change `Aliyun` registry for Enterprise one.

## [0.4.0] - 2023-01-23

### Added

- Push to `gcp` and `cloud-director` app collection.
- Add `external-secrets` related policies that restrict the usage of `*giantswarm*` namespaces service account for secret stores using the kubernetes provider.

### Changed

- Remove deprecated `validate` step from CI.

## [0.3.0] - 2022-11-29

### Added

- Actually added the `crossplane` checks to the Helm chart

### Changed

- Split deprecated CRD usage checks per kubernetes version and added Helm kubernetes version check condition to them because kyverno fails if those CRDs do not exist anymore (e.g. the cluster was upgraded beyond that version)

## [0.2.0] - 2022-11-17

### Added

- Add `ClusterPolicy` to allow managing `pkg.crossplane.io/v1/Provider` only to subject in the `giantswarm:giantswarm:giantswarm-admins` group or with the `cluster-admin` cluster role

## [0.1.1] - 2022-08-05

## [0.1.0] - 2022-04-08

### Added

- Add `restrict-image-registries` audit policy to ensure images come from trusted Giant Swarm registries.

## [0.0.1] - 2022-04-01

### Added

- Initial policies moved from [`kyverno-policies`](https://github.com/giantswarm/kyverno-policies).
- Push to AWS, KVM, and OpenStack collections.

[Unreleased]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.8.3...HEAD
[0.8.3]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.8.2...v0.8.3
[0.8.2]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.7.2...v0.8.0
[0.7.2]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.7.1...v0.7.2
[0.7.1]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.5...v0.5.0
[0.4.5]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.4...v0.4.5
[0.4.4]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.3...v0.4.4
[0.4.3]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/giantswarm/kyverno-policies-dx/releases/tag/v0.0.1
