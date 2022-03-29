import sys
sys.path.append('../../../tests')

import yaml
from functools import partial
import time
import random
import string
import ensure
from textwrap import dedent

from ensure import release
from ensure import cluster
from ensure import machinedeployment
from ensure import kubeadmconfig
from ensure import kubeadmconfig_controlplane
from ensure import kubeadmconfig_with_labels
from ensure import kubeadmconfig_with_role_labels
from ensure import kubeadmconfig_with_kubelet_args
from ensure import kubeadm_control_plane
from ensure import kubeadmconfig_controlplane
from ensure import kubeadmconfig_with_files
from ensure import kubeadmconfig_with_audit_file

import pytest
from pytest_kube import forward_requests, wait_for_rollout, app_template

import logging
LOGGER = logging.getLogger(__name__)

@pytest.mark.smoke
def test_kubeadmconfig_policy_controlplane(kubeadmconfig_controlplane) -> None:
    """
    test_kubeadmconfig_policy_controlplane tests defaulting of a KubeadmConfig for a control plane where all required values are empty strings.

    :param kubeadmconfig_controlplane: KubeadmConfig CR which is empty.
    """
    assert kubeadmconfig_controlplane['metadata']['labels']['cluster.x-k8s.io/watch-filter'] == ensure.watch_label
    assert kubeadmconfig_controlplane['metadata']['labels']['cluster.x-k8s.io/control-plane'] == ""

@pytest.mark.smoke
def test_kubeadmconfig_auditpolicy(kubeadmconfig_with_files) -> None:
    """
    test_kubeadmconfig_auditpolicy tests defaulting of a kubeadmconfig with audit policy details

    :param kubeadmconfig_with_files: KubeadmConfig CR which includes some existing files
    """
    found = False
    for file in kubeadmconfig_with_files['spec']['files']:
        if file['path'] == "/etc/kubernetes/policies/audit-policy.yaml":
            found = True

    assert found == True

@pytest.mark.smoke
def test_kubeadmconfig_auditpolicy(kubeadmconfig_with_audit_file) -> None:
    """
    test_kubeadmconfig_auditpolicy tests defaulting of a kubeadmconfig with audit policy details

    :param kubeadmconfig_with_audit_file: KubeadmConfig CR which includes an existing audit file
    """
    assert len(kubeadmconfig_with_audit_file['spec']['files']) == 1
