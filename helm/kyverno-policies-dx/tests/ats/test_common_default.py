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
from ensure import fetch_policies
from ensure import run_pod_from_registries

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

@pytest.mark.smoke
def test_kyverno_policy(fetch_policies) -> None:
    """
    test_kyverno_policy tests that the policy is present
    """
    found = False
    
    for policy in fetch_policies['items']:
        LOGGER.info(f"Policy {policy['metadata']['name']} is present in the cluster")
        if policy['metadata']['name'] == "restrict-image-registries":
            found = True
    
    assert found == True

@pytest.mark.smoke
def test_kyverno_policy_reports(run_pod_outside_gs) -> None:
    """
    test_kyverno_policy_reports tests the restrict-image-registries policy

    :param run_pod_outside_gs: Pod with a container from outside GS registries
    """

    bad_registry_found = False
    good_registry_found = False

    if len(run_pod_outside_gs['items']) == 0:
        LOGGER.warning("No policy reports present on the cluster")

    for report in run_pod_outside_gs['items']:
        LOGGER.info(f"Policy report {report['metadata']['name']} is present on the cluster")

        for policy_report in report['results']:
            LOGGER.info(f"Policy report for Policy {policy_report['policy']} is present on the cluster")

            if policy_report['policy'] == "restrict-image-registries":

                for resource in policy_report['resources']:
                    LOGGER.info(f"PolicyReport for Policy {policy_report['policy']} for resource {resource['name']} is present on the cluster")

                    if resource['name'] == "pod-outside-gs-registries":
                        
                        if policy_report['result'] == "fail":
                            bad_registry_found = True
                            break
                        else:
                            LOGGER.warning(f"PolicyReport for {resource['name']} is present but result is not correct")

                    if resource['name'] == "pod-inside-gs-registries":
                        
                        if policy_report['result'] == "pass":
                            good_registry_found = True
                            break
                        else:
                            LOGGER.warning(f"PolicyReport for {resource['name']} is present but result is not correct")

    assert found == True
