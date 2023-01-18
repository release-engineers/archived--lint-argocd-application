import os
import sys
import subprocess
import hashlib


def repository_dir(repository_url):
    """
    Returns the directory where a repository would be cloned to.
    :param repository_url:
    :return:
    """
    local_dir = sys.path[0]
    cache_dir = os.path.join(local_dir, "cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    sha256 = hashlib.sha256()
    sha256.update(repository_url.encode("utf-8"))
    digest = sha256.digest()
    return os.path.join(cache_dir, digest.hex())


def rule_metadata_name(document):
    if "metadata" not in document:
        raise Exception("missing .metadata")
    if "name" not in document["metadata"]:
        raise Exception("missing .metadata.name")
    return [rule_source_repo_accessible]


def rule_metadata_finalizer(document):
    if "metadata" not in document:
        raise Exception("missing .metadata")
    if "finalizers" not in document["metadata"]:
        raise Exception("missing .metadata.finalizers")
    if "resources-finalizer.argocd.argoproj.io" not in document["metadata"]["finalizers"]:
        raise Exception("missing .metadata.finalizers does not contain resources-finalizer.argocd.argoproj.io")
    return []


def rule_destination_namespace(document):
    if "spec" not in document:
        raise Exception("missing .spec")
    if "destination" not in document["spec"]:
        raise Exception("missing .spec.destination")
    if "namespace" not in document["spec"]["destination"]:
        raise Exception("missing .spec.destination.namespace")
    if "syncPolicy" in document["spec"]:
        if "syncOptions" in document["spec"]["syncPolicy"]:
            if "CreateNamespace=true" in document["spec"]["syncPolicy"]["syncOptions"]:
                return
    # TODO: verify namespace exists
    return []


def rule_destination_server(document):
    if "spec" not in document:
        raise Exception("missing .spec")
    if "destination" not in document["spec"]:
        raise Exception("missing .spec.destination")
    if "server" not in document["spec"]["destination"]:
        raise Exception("missing .spec.destination.server")
    # TODO: verify server exists
    return []


def rule_project_exists(document):
    if "spec" not in document:
        raise Exception("missing .spec")
    if "project" not in document["spec"]:
        raise Exception("missing .spec.project")
    # TODO: verify project exists
    return [rule_project_exists_and_namespace_allowed, rule_project_exists_and_server_allowed]


def rule_project_exists_and_namespace_allowed(document):
    project = document["spec"]["project"]
    # TODO: verify project allows for deployment into .spec.destination.namespace
    return []


def rule_project_exists_and_server_allowed(document):
    project = document["spec"]["project"]
    # TODO: verify project allows for deployment into .spec.destination.server
    return []


def rule_source_repo_accessible(document):
    if "spec" not in document:
        raise Exception("missing .spec")
    if "source" not in document["spec"]:
        raise Exception("missing .spec.source")
    if "repoURL" not in document["spec"]["source"]:
        raise Exception("missing .spec.source.repoURL")

    # git clone ${repoURL}
    repo_url = document["spec"]["source"]["repoURL"]
    repo_dir = repository_dir(repo_url)
    if not os.path.exists(repo_dir):
        result_clone = subprocess.run(["git", "clone", repo_url, repo_dir],
                                      stdout=sys.stdout,
                                      stderr=sys.stdout)
        if result_clone.returncode != 0:
            raise Exception(".spec.source.repoURL '{}' could not be cloned with git".format(repo_url))

    # git fetch
    result_fetch = subprocess.run(["git", "fetch", "--all"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  cwd=repo_dir)
    if result_fetch.returncode != 0:
        raise Exception(".spec.source.repoURL '{}' could not be fetched with git".format(repo_url))

    return [rule_source_repo_revision_accessible]


def rule_source_repo_revision_accessible(document):
    source = document["spec"]["source"]
    if "targetRevision" not in source:
        raise Exception("missing .spec.source.targetRevision")

    # git checkout ${targetRevision}
    # TODO: ensure local repository points to most recent targetRevision on origin
    repo_url = source["repoURL"]
    repo_ref = source["targetRevision"]
    repo_dir = repository_dir(repo_url)
    result_checkout = subprocess.run(["git", "checkout", repo_ref],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     cwd=repo_dir)
    if result_checkout.returncode != 0:
        raise Exception(".spec.source.targetRevision '{}' could not be checked out with git for repo '{}'"
                        .format(repo_ref, repo_url))

    return [rule_source_repo_revision_path_accessible]


def rule_source_repo_revision_path_accessible(document):
    source = document["spec"]["source"]
    if "path" not in source:
        raise Exception("missing .spec.source.path")
    source_path = source["path"]
    repo_url = source["repoURL"]
    repo_ref = source["targetRevision"]
    repo_dir = repository_dir(repo_url)
    repo_dir_path = os.path.join(repo_dir, source_path)

    # ensure repo_dir_path is a subdirectory of repo_dir
    if not os.path.commonpath([repo_dir_path, repo_dir]) == repo_dir:
        raise Exception(
            ".spec.source.path '{}' does not resolve to a subdirectory of '{}'".format(source_path, repo_url))

    # ensure repo_dir_path exists
    if not os.path.exists(repo_dir_path):
        raise Exception(".spec.source.path '{}' does not exist in repo '{}' at revision '{}'"
                        .format(source_path, repo_url, repo_ref))

    # delegate to rules for explicitly specified tools
    if "helm" in source:
        return [rule_source_explicit_type_helm]
    if "kustomize" in source:
        return [rule_source_explicit_type_kustomize]
    if "directory" in source:
        return [rule_source_explicit_type_directory]
    if "plugin" in source:
        return []

    # delegate to rules for detected tools based on ArgoCD's tool detection
    # (see https://github.com/argoproj/argo-cd/blob/1808539652f84b276b8c321ef213d82ae47e1c1b/docs/user-guide/tool_detection.md)
    files = os.listdir(repo_dir_path)
    if "Chart.yaml" in files:
        return [rule_source_content_helm]
    if "kustomization.yaml" in files or "kustomization.yml" in files or "Kustomization" in files:
        return [rule_source_content_kustomize]
    return [rule_source_content_directory]


def rule_source_explicit_type_helm(document):
    source = document["spec"]["source"]
    if "kustomize" in source:
        raise Exception("cannot specify both .spec.source.helm and .spec.source.kustomize")
    if "directory" in source:
        raise Exception("cannot specify both .spec.source.helm and .spec.source.directory")
    return [rule_source_content_helm]


def rule_source_explicit_type_kustomize(document):
    source = document["spec"]["source"]
    if "helm" in source:
        raise Exception("cannot specify both .spec.source.kustomize and .spec.source.helm")
    if "directory" in source:
        raise Exception("cannot specify both .spec.source.kustomize and .spec.source.directory")
    return [rule_source_content_kustomize]


def rule_source_explicit_type_directory(document):
    source = document["spec"]["source"]
    if "helm" in source:
        raise Exception("cannot specify both .spec.source.directory and .spec.source.helm")
    if "kustomize" in source:
        raise Exception("cannot specify both .spec.source.directory and .spec.source.kustomize")
    return [rule_source_content_directory]


def rule_source_content_helm(document):
    source = document["spec"]["source"]
    source_path = source["path"]
    repo_url = source["repoURL"]
    repo_ref = source["targetRevision"]
    repo_dir = repository_dir(repo_url)
    repo_dir_path = os.path.join(repo_dir, source_path)
    application_name = document["metadata"]["name"]

    # helm template ${application_name} ${repo_dir_path}
    # TODO: pass value files referenced in Application
    result_helm_template = subprocess.run(["helm", "template", application_name, repo_dir_path],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          cwd=repo_dir_path)
    if result_helm_template.returncode != 0:
        raise Exception(
            "helm template failed for repo '{}' at revision '{}' in path '{}' with release name '{}'. Full error output: {}"
            .format(repo_url, repo_ref, source_path, application_name, result_helm_template.stderr))

    # kubectl apply --dry-run -f -
    result_kubectl_apply = subprocess.run(["kubectl", "apply", "--dry-run=client", "-f", "-"],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          input=result_helm_template.stdout)
    if result_kubectl_apply.returncode != 0:
        raise Exception(
            "kubectl apply --dry-run failed for repo '{}' at revision '{}' in path '{}' with release name '{}'. Full error output: {}"
            .format(repo_url, repo_ref, source_path, application_name, result_kubectl_apply.stderr))

    return []


def rule_source_content_kustomize(document):
    # TODO: verify kustomize build into kubectl validation works
    return []


def rule_source_content_directory(document):
    # TODO: verify kubectl validation works
    return []


top = [
    rule_metadata_name,
    rule_metadata_finalizer,
    rule_destination_namespace,
    rule_destination_server,
    rule_project_exists
]
