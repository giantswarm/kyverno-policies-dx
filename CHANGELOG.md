# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Push to `vsphere` app collection.
- Don't push to `openstack` app collection.

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

[Unreleased]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.2...HEAD
[0.4.2]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/giantswarm/kyverno-policies-dx/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/giantswarm/kyverno-policies-dx/releases/tag/v0.0.1
