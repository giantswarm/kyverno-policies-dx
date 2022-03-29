import yaml
from functools import partial
import time
import random
import string
from textwrap import dedent

import pytest
from pytest_kube import forward_requests, wait_for_rollout, app_template

import logging
LOGGER = logging.getLogger(__name__)

service_monitor_name = "test-service-monitor"
silence_name = "test-silence"
cluster_name = "test-cluster"
machinepool_name = "mp0"
release_version = "20.0.0-alpha1"
cluster_apps_operator_version = "2.0.0"
watch_label = "capi"

# Giant Swarm specific fixtures

@pytest.fixture(scope="module")
def release(kubernetes_cluster):
    r = dedent(f"""
        apiVersion: release.giantswarm.io/v1alpha1
        kind: Release
        metadata:
          creationTimestamp: null
          name: v{release_version}
        spec:
          apps:
          - name: calico
            version: 0.2.0
            componentVersion: 3.18.0
          - name: cert-exporter
            version: 1.6.0
          components:
          - name: cluster-api-bootstrap-provider-kubeadm
            version: 0.0.1
          - name: cluster-api-control-plane
            version: 0.0.1
          - name: cluster-api-core
            version: 0.0.1
          - name: cluster-api-provider-aws
            version: 0.0.1
          - name: cluster-apps-operator
            version: {cluster_apps_operator_version}
          date: "2021-03-22T14:50:41Z"
          state: active
        status:
          inUse: false
          ready: false
    """)

    kubernetes_cluster.kubectl("apply", input=r, output=None)
    LOGGER.info(f"Release v{release_version} applied")

    raw = kubernetes_cluster.kubectl(
        f"get release v{release_version}", output="yaml")

    release = yaml.safe_load(raw)

    yield release

    kubernetes_cluster.kubectl(f"delete release v{release_version}", output=None)
    LOGGER.info(f"Release v{release_version} deleted")

# Silence fixtures

@pytest.fixture
def silence(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: monitoring.giantswarm.io/v1alpha1
        kind: Silence
        metadata:
          name: {silence_name}
          namespace: default
        spec:
          matchers: []
          targetTags: []
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"Silence {silence_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get silences {silence_name}", output="yaml")

    silence = yaml.safe_load(raw)

    yield silence

    kubernetes_cluster.kubectl(f"delete silence {silence_name}", output=None)
    LOGGER.info(f"Silence {silence_name} deleted")

@pytest.fixture
def silence_with_matchers(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: monitoring.giantswarm.io/v1alpha1
        kind: Silence
        metadata:
          name: {silence_name}
          namespace: default
        spec:
          matchers:
          - isEqual: false
            isRegex: false
            name: test
            value: test
          targetTags: []
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"Silence {silence_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get silences {silence_name}", output="yaml")

    silence = yaml.safe_load(raw)

    yield silence

    kubernetes_cluster.kubectl(f"delete silence {silence_name}", output=None)
    LOGGER.info(f"Silence {silence_name} deleted")

@pytest.fixture
def kubeadm_control_plane(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: controlplane.cluster.x-k8s.io/v1alpha4
        kind: KubeadmControlPlane
        metadata:
          labels:
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: capi
          name: {cluster_name}
          namespace: default
        spec:
          kubeadmConfigSpec:
            clusterConfiguration:
              apiServer:
                extraArgs:
                  cloud-config: /etc/kubernetes/azure.json
                  cloud-provider: azure
                extraVolumes:
                - hostPath: /etc/kubernetes/azure.json
                  mountPath: /etc/kubernetes/azure.json
                  name: cloud-config
                  readOnly: true
              controllerManager:
                extraArgs:
                  allocate-node-cidrs: "false"
          machineTemplate:
            infrastructureRef:
              apiVersion: infrastructure.cluster.x-k8s.io/v1alpha4
              kind: AWSMachineTemplate
              name: {cluster_name}
          version: 1.22.0
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"KubeadmControlPlane {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get kubeadmcontrolplane {cluster_name}", output="yaml")

    kcp = yaml.safe_load(raw)

    yield kcp

    kubernetes_cluster.kubectl(f"delete kubeadmcontrolplane {cluster_name}", output=None)
    LOGGER.info(f"kubeadmcontrolplane {cluster_name} deleted")
