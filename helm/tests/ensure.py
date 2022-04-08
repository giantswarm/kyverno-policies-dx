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

# CAPI Core fixtures


@pytest.fixture
def cluster(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: cluster.x-k8s.io/v1alpha3
        kind: Cluster
        metadata:
          name: {cluster_name}
          namespace: default
          labels:
            release.giantswarm.io/version: {release_version}
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
        spec:
          clusterNetwork:
            pods:
              cidrBlocks:
                - 192.168.0.0/16
          controlPlaneRef:
            apiVersion: controlplane.cluster.x-k8s.io/v1alpha3
            kind: KubeadmControlPlane
            name: {cluster_name}-control-plane
          infrastructureRef:
            apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
            kind: AWSCluster
            name: {cluster_name}
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"Cluster {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get cluster {cluster_name}", output="yaml")

    cluster = yaml.safe_load(raw)

    yield cluster

    kubernetes_cluster.kubectl(f"delete cluster {cluster_name}", output=None)
    LOGGER.info(f"Cluster {cluster_name} deleted")


@pytest.fixture
def cluster_v1alpha4(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: cluster.x-k8s.io/v1alpha4
        kind: Cluster
        metadata:
          name: {cluster_name}
          namespace: default
          labels:
            release.giantswarm.io/version: {release_version}
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
        spec:
          clusterNetwork:
            pods:
              cidrBlocks:
                - 192.168.0.0/16
          controlPlaneRef:
            apiVersion: controlplane.cluster.x-k8s.io/v1alpha4
            kind: KubeadmControlPlane
            name: {cluster_name}-control-plane
          infrastructureRef:
            apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
            kind: AWSCluster
            name: {cluster_name}
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"Cluster {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get cluster {cluster_name}", output="yaml")

    cluster = yaml.safe_load(raw)

    yield cluster

    kubernetes_cluster.kubectl(f"delete cluster {cluster_name}", output=None)
    LOGGER.info(f"Cluster {cluster_name} deleted")


@pytest.fixture
def machinedeployment(kubernetes_cluster):
    md = dedent(f"""
        apiVersion: cluster.x-k8s.io/v1alpha3
        kind: MachineDeployment
        metadata:
          name: {cluster_name}
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
        spec:
          clusterName: {cluster_name}
          replicas: 1
          selector:
            matchLabels:
              clusterName: {cluster_name}
          template:
            metadata:
              labels:
                clusterName: {cluster_name}
            spec:
              bootstrap:
                configRef:
                  apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
                  kind: KubeadmConfigTemplate
                  name: {cluster_name}
              clusterName: {cluster_name}
              infrastructureRef:
                apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
                kind: AWSMachineTemplate
                name: {cluster_name}
              version: v1.19.7
    """)

    kubernetes_cluster.kubectl("apply", input=md, output=None)
    LOGGER.info(f"MachineDeployment {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get machinedeployment {cluster_name}", output="yaml")

    machinedeployment = yaml.safe_load(raw)

    yield machinedeployment

    kubernetes_cluster.kubectl(f"delete machinedeployment {cluster_name}", output=None)
    LOGGER.info(f"MachineDeployment {cluster_name} deleted")


@pytest.fixture
def kubeadmconfig(kubernetes_cluster):
    md = dedent(f"""
        apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
        kind: KubeadmConfig
        metadata:
          name: {cluster_name}
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: {watch_label}
    """)

    kubernetes_cluster.kubectl("apply", input=md, output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get kubeadmconfig {cluster_name}", output="yaml")

    kubeadmconfig = yaml.safe_load(raw)

    yield kubeadmconfig

    kubernetes_cluster.kubectl(f"delete kubeadmconfig {cluster_name}", output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} deleted")


@pytest.fixture
def kubeadmconfig_with_labels(kubernetes_cluster):
    md = dedent(f"""
        apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
        kind: KubeadmConfig
        metadata:
          name: {cluster_name}
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: {watch_label}
        spec:
          joinConfiguration:
            nodeRegistration:
              kubeletExtraArgs:
                node-labels: mylabel=test
    """)

    kubernetes_cluster.kubectl("apply", input=md, output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get kubeadmconfig {cluster_name}", output="yaml")

    kubeadmconfig = yaml.safe_load(raw)

    yield kubeadmconfig

    kubernetes_cluster.kubectl(f"delete kubeadmconfig {cluster_name}", output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} deleted")


@pytest.fixture
def kubeadmconfig_with_files(kubernetes_cluster):
    md = dedent(f"""
        apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
        kind: KubeadmConfig
        metadata:
          name: {cluster_name}
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: {watch_label}
        spec:
          files:
          - content: ""
            encoding: base64
            owner: root
            path: /etc/ssh/sshd_config
            permissions: "640"
    """)

    kubernetes_cluster.kubectl("apply", input=md, output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get kubeadmconfig {cluster_name}", output="yaml")

    kubeadmconfig = yaml.safe_load(raw)

    yield kubeadmconfig

    kubernetes_cluster.kubectl(f"delete kubeadmconfig {cluster_name}", output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} deleted")


@pytest.fixture
def kubeadmconfig_with_audit_file(kubernetes_cluster):
    md = dedent(f"""
        apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
        kind: KubeadmConfig
        metadata:
          name: {cluster_name}
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: {watch_label}
        spec:
          files:
          - content: ""
            encoding: base64
            owner: root
            path: /etc/kubernetes/policies/audit-policy.yaml
            permissions: "640"
    """)

    kubernetes_cluster.kubectl("apply", input=md, output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get kubeadmconfig {cluster_name}", output="yaml")

    kubeadmconfig = yaml.safe_load(raw)

    yield kubeadmconfig

    kubernetes_cluster.kubectl(f"delete kubeadmconfig {cluster_name}", output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} deleted")


@pytest.fixture
def kubeadmconfig_with_role_labels(kubernetes_cluster):
    md = dedent(f"""
        apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
        kind: KubeadmConfig
        metadata:
          name: {cluster_name}
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: {watch_label}
        spec:
          joinConfiguration:
            nodeRegistration:
              kubeletExtraArgs:
                node-labels: role=emperor,mylabel=test
    """)

    kubernetes_cluster.kubectl("apply", input=md, output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get kubeadmconfig {cluster_name}", output="yaml")

    kubeadmconfig = yaml.safe_load(raw)

    yield kubeadmconfig

    kubernetes_cluster.kubectl(f"delete kubeadmconfig {cluster_name}", output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} deleted")


@pytest.fixture
def kubeadmconfig_with_kubelet_args(kubernetes_cluster):
    md = dedent(f"""
        apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
        kind: KubeadmConfig
        metadata:
          name: {cluster_name}
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: {watch_label}
        spec:
          joinConfiguration:
            nodeRegistration:
              kubeletExtraArgs:
                v: "1"
                image-pull-progress-deadline: 1m
    """)

    kubernetes_cluster.kubectl("apply", input=md, output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get kubeadmconfig {cluster_name}", output="yaml")

    kubeadmconfig = yaml.safe_load(raw)

    yield kubeadmconfig

    kubernetes_cluster.kubectl(f"delete kubeadmconfig {cluster_name}", output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} deleted")


@pytest.fixture
def kubeadmconfig_controlplane(kubernetes_cluster):
    md = dedent(f"""
        apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
        kind: KubeadmConfig
        metadata:
          name: {cluster_name}
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: {watch_label}
            cluster.x-k8s.io/control-plane: ""
    """)

    kubernetes_cluster.kubectl("apply", input=md, output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get kubeadmconfig {cluster_name}", output="yaml")

    kubeadmconfig = yaml.safe_load(raw)

    yield kubeadmconfig

    kubernetes_cluster.kubectl(f"delete kubeadmconfig {cluster_name}", output=None)
    LOGGER.info(f"KubeadmConfig {cluster_name} deleted")

# CAPA fixtures


@pytest.fixture
def awscluster_v1alpha3(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
        kind: AWSCluster
        metadata:
          name: {cluster_name}
          namespace: default
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
        spec:
          region: ""
          sshKeyName: ""
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"AWSCluster {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get awsclusters.v1alpha3.infrastructure.cluster.x-k8s.io {cluster_name}", output="yaml")

    awscluster = yaml.safe_load(raw)

    yield awscluster

    kubernetes_cluster.kubectl(f"delete awscluster {cluster_name}", output=None)
    LOGGER.info(f"AWSCluster {cluster_name} deleted")


@pytest.fixture
def awscluster_v1alpha3_empty(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
        kind: AWSCluster
        metadata:
          name: {cluster_name}
          namespace: default
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"AWSCluster {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get awsclusters.v1alpha3.infrastructure.cluster.x-k8s.io {cluster_name}", output="yaml")

    awscluster = yaml.safe_load(raw)

    yield awscluster

    kubernetes_cluster.kubectl(f"delete awscluster {cluster_name}", output=None)
    LOGGER.info(f"AWSCluster {cluster_name} deleted")


@pytest.fixture
def awscluster_v1alpha3_empty_labeled(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
        kind: AWSCluster
        metadata:
          name: {cluster_name}
          namespace: default
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
            cluster.x-k8s.io/watch-filter: {watch_label}
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"AWSCluster {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get awsclusters.v1alpha3.infrastructure.cluster.x-k8s.io {cluster_name}", output="yaml")

    awscluster = yaml.safe_load(raw)

    yield awscluster

    kubernetes_cluster.kubectl(f"delete awscluster {cluster_name}", output=None)
    LOGGER.info(f"AWSCluster {cluster_name} deleted")


@pytest.fixture
def awsmachinetemplate(kubernetes_cluster):
    c = dedent(f"""
      apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
      kind: AWSMachineTemplate
      metadata:
        labels:
          cluster.x-k8s.io/cluster-name: {cluster_name}
          cluster.x-k8s.io/watch-filter: {watch_label}
          giantswarm.io/cluster: {cluster_name}
        name: {cluster_name}
        namespace: default
      spec:
        template:
          spec:
            iamInstanceProfile: control-plane-{cluster_name}
            sshKeyName: ""
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"AWSMachineTemplate {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get AWSMachineTemplates {cluster_name}", output="yaml")

    awsmachinetemplate = yaml.safe_load(raw)

    yield awsmachinetemplate

    kubernetes_cluster.kubectl(f"delete AWSMachineTemplate {cluster_name}", output=None)
    LOGGER.info(f"AWSMachineTemplate {cluster_name} deleted")


@pytest.fixture
def awsmachinepool(kubernetes_cluster):
    c = dedent(f"""
      apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
      kind: AWSMachinePool
      metadata:
        labels:
          cluster.x-k8s.io/cluster-name: {cluster_name}
          cluster.x-k8s.io/watch-filter: capi
          giantswarm.io/cluster: {cluster_name}
          giantswarm.io/machine-pool: {cluster_name}
        name: {cluster_name}
        namespace: default
      spec:
        availabilityZones:
        - eu-west-1a
        awsLaunchTemplate:
          iamInstanceProfile: nodes-{cluster_name}-{cluster_name}
          instanceType: m5.xlarge
          sshKeyName: ""
        maxSize: 2
        minSize: 2
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"AWSMachinePool {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get AWSMachinePools {cluster_name}", output="yaml")

    awsmachinepool = yaml.safe_load(raw)

    yield awsmachinepool

    kubernetes_cluster.kubectl(f"delete AWSMachinePool {cluster_name}", output=None)
    LOGGER.info(f"AWSMachinePool {cluster_name} deleted")


@pytest.fixture
def awsclusterroleidentity(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: infrastructure.cluster.x-k8s.io/v1alpha3
        kind: AWSClusterRoleIdentity
        metadata:
          labels:
            cluster.x-k8s.io/watch-filter: {watch_label}
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
          name: {cluster_name}
          namespace: default
        spec:
          allowedNamespaces:
            list:
            - org-marcel
          roleARN: ""
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"AWSClusterRoleIdentity {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get AWSClusterRoleIdentity {cluster_name}", output="yaml")

    awsclusterroleidentity = yaml.safe_load(raw)

    yield awsclusterroleidentity

    kubernetes_cluster.kubectl(f"delete AWSClusterRoleIdentity {cluster_name}", output=None)
    LOGGER.info(f"AWSClusterRoleIdentity {cluster_name} deleted")

# CAPZ fixtures


@pytest.fixture
def azurecluster(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: infrastructure.cluster.x-k8s.io/v1alpha4
        kind: AzureCluster
        metadata:
          name: {cluster_name}
          namespace: default
          labels:
            giantswarm.io/cluster: {cluster_name}
            cluster.x-k8s.io/cluster-name: {cluster_name}
        spec:
          location: ""
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"AzureCluster {cluster_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get azurecluster {cluster_name}", output="yaml")

    azurecluster = yaml.safe_load(raw)

    yield azurecluster

    kubernetes_cluster.kubectl(f"delete azurecluster {cluster_name}", output=None)
    LOGGER.info(f"AzureCluster {cluster_name} deleted")


@pytest.fixture
def azuremachinepool(kubernetes_cluster):
    c = dedent(f"""
        apiVersion: infrastructure.cluster.x-k8s.io/v1alpha4
        kind: AzureMachinePool
        metadata:
          name: {machinepool_name}
          namespace: default
          labels:
            "cluster.x-k8s.io/cluster-name": {cluster_name}
            "giantswarm.io/cluster": {cluster_name}
        spec:
          identity: SystemAssigned
          location: ""
          strategy:
            rollingUpdate:
              deletePolicy: Oldest
              maxSurge: 25%
              maxUnavailable: 1
            type: RollingUpdate
          template:
            osDisk:
              diskSizeGB: 30
              managedDisk:
                storageAccountType: Premium_LRS
              osType: Linux
            sshPublicKey: ""
            vmSize: Standard_D4s_v3
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"AzureMachinePool {machinepool_name} applied")

    raw = kubernetes_cluster.kubectl(
        f"get AzureMachinePool {machinepool_name}", output="yaml")

    azuremachinepool = yaml.safe_load(raw)

    yield azuremachinepool

    kubernetes_cluster.kubectl(f"delete azuremachinepool {machinepool_name}", output=None)
    LOGGER.info(f"AzureMachinePool {machinepool_name} deleted")

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

# Kyverno fixtures


@pytest.fixture
def fetch_policies(kubernetes_cluster):
    raw = kubernetes_cluster.kubectl(
        f"get cpol", output="yaml")

    kcp = yaml.safe_load(raw)

    yield kcp


@pytest.fixture
def run_pod_from_registries(kubernetes_cluster):
    bad_pod_name = "pod-outside-gs-registries"
    good_pod_name = "pod-inside-gs-registries"

    # Create a Pod with a known bad registry
    c = dedent(f"""
        apiVersion: v1
        kind: Pod
        metadata:
          labels:
            cluster.x-k8s.io/cluster-name: {cluster_name}
          name: {bad_pod_name}
          namespace: default
        spec:
          containers:
          - name: bad-registry
            image: docker.io/nginx
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"Pod {bad_pod_name} applied")

    # Create a Pod with all the known good registries
    c = dedent(f"""
        apiVersion: v1
        kind: Pod
        metadata:
          labels:
            cluster.x-k8s.io/cluster-name: {cluster_name}
          name: {good_pod_name}
          namespace: default
        spec:
          containers:
          - name: good-registry-quay
            image: quay.io/giantswarm/nginx
          - name: good-registry-docker
            image: docker.io/giantswarm/nginx
          - name: good-registry-gs
            image: giantswarm/nginx
          - name: good-registry-azurecr
            image: giantswarm.azurecr.io/giantswarm/nginx
          - name: good-registry-aliyuncs
            image: registry-intl.cn-shanghai.aliyuncs.com/giantswarm/nginx
    """)

    kubernetes_cluster.kubectl("apply", input=c, output=None)
    LOGGER.info(f"Pod {good_pod_name} applied")

    # Wait for a PolicyReport to be created
    timeout = 0
    reports_found = False

    while timeout < 5 and not reports_found:
        raw = kubernetes_cluster.kubectl(
            f"get polr", output="yaml")

        polr = yaml.safe_load(raw)

        if len(polr['items']) == 0:
            time.sleep(15)
            timeout += 1
        else:
            # Check that there is one result for each pod
            for report in polr['items']:
                LOGGER.info(f"Report {report['metadata']['name']} has {len(report['results'])} results")

                if len(report['results']) != 2:
                    time.sleep(15)
                    timeout += 1
                else:
                    reports_found = True
                    break

    yield polr

    kubernetes_cluster.kubectl(f"delete pod {good_pod_name} {bad_pod_name}", output=None)
    LOGGER.info(f"Pods {good_pod_name}, {bad_pod_name} deleted")
