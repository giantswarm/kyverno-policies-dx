import json
import logging
import shutil
import time
from typing import Any

import pykube
import pytest
import requests
import yaml
from pykube import HTTPClient
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.giantswarm_app_platform.app import (
    AppCR,
    AppFactoryFunc,
    ConfiguredApp,
)
from pytest_helm_charts.k8s.deployment import wait_for_deployments_to_run
from pytest_helm_charts.k8s.namespace import ensure_namespace_exists

logger = logging.getLogger(__name__)

timeout: int = 600
kyverno_app_version = "0.13.0"
app_catalog_url = "https://giantswarm.github.io/giantswarm-catalog/"
kyverno_namespace = "default"
kyverno_app_name = "kyverno"
kyverno_policies_app_name = "kyverno-policies-dx"


@pytest.fixture(scope="module")
def kyverno_app_cr(
    kube_cluster: Cluster, app_factory: AppFactoryFunc
) -> ConfiguredApp:
    # app platform is too slow to correctly delete AppCatalog between 'smoke' and 'functional' runs,
    # so to work-around we're adding test type to the name of the created AppCatalog
    # FIXME: this should be provided by the pytest-helm-chart lib, will be fixed there
    #  after that, it can be removed here
    ensure_namespace_exists(kube_cluster.kube_client, kyverno_namespace)
    res = app_factory(
        kyverno_app_name,
        kyverno_app_version,
        f"giantswarm-stable",
        kyverno_namespace,
        app_catalog_url,
        timeout_sec=timeout,
        namespace=kyverno_namespace,
        deployment_namespace=kyverno_namespace,
    )
    logger.info("Kyverno App CR set")
    return res


# As the fixture doesn't detect nor manage pre-created appCatalogs,
# it can't manage the one created earlier apptestctl.
# We're registering the same catalog here, just with different name to avoid name conflict.
@pytest.fixture(scope="module")
def kyverno_policies_app_cr(
    app_factory: AppFactoryFunc, chart_version: str, kyverno_app_cr: ConfiguredApp
) -> ConfiguredApp:
    res = app_factory(
        kyverno_policies_app_name,
        chart_version,
        f"chartmuseum-test-time",
        "default",
        "http://chartmuseum-chartmuseum:8080/charts/",
        timeout_sec=timeout,
        namespace="default",
        deployment_namespace="default",
    )
    logger.info("Kyverno Policies App CR set")
    return res

@pytest.mark.smoke
def test_api_working(kube_cluster: Cluster) -> None:
    """
    Test if the kubernetes api works
    """
    assert kube_cluster.kube_client is not None
    assert len(pykube.Node.objects(kube_cluster.kube_client)) >= 1

@pytest.mark.smoke
def dummy_test(kube_cluster: Cluster) -> None:
    """
    Just check things
    """

    logger.info(kube_cluster.kubectl(
        "get deploy -n kyverno"
    ))

    logger.info(kube_cluster.kubectl(
        "get deploy"
    ))

    logger.info(kube_cluster.kubectl(
        "get app -A"
    ))

    assert true

# @pytest.mark.smoke
# def test_kyverno_app_deployed(kube_cluster: Cluster, kyverno_app_cr: AppCR):
#     """
#     Test if Kyverno is deployed
#     """
#     app_cr = (
#         AppCR.objects(kube_cluster.kube_client)
#         .filter(namespace=kyverno_namespace)
#         .get_by_name(kyverno_app_name)
#     )
#     app_version = app_cr.obj["status"]["version"]
#     wait_for_deployments_to_run(
#         kube_cluster.kube_client,
#         kyverno_app_name,
#         kyverno_namespace,
#         timeout,
#     )
#     assert app_version == kyverno_app_version
#     logger.info(f"Kyverno App CR shows installed appVersion {app_version}")
