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
    # TODO: verify repoURL accessible
    return [rule_source_repo_revision_accessible]


def rule_source_repo_revision_accessible(document):
    source = document["spec"]["source"]
    if "targetRevision" not in source:
        raise Exception("missing .spec.source.targetRevision")
    # TODO: verify targetRevision exists in repository
    return [rule_source_repo_revision_path_accessible]


def rule_source_repo_revision_path_accessible(document):
    source = document["spec"]["source"]
    if "path" not in source:
        raise Exception("missing .spec.source.path")
    # TODO: verify path exists in repository at targetRevision
    if "helm" in source:
        return [rule_source_explicit_type_helm]
    if "kustomize" in source:
        return [rule_source_explicit_type_kustomize]
    if "directory" in source:
        return [rule_source_explicit_type_directory]
    return [rule_source_type_discovery]


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
    return [rule_source_content_kubernetes]


def rule_source_type_discovery(document):
    # see https://github.com/argoproj/argo-cd/blob/1808539652f84b276b8c321ef213d82ae47e1c1b/docs/user-guide/tool_detection.md
    # TODO: detect Helm by presence of Chart.yaml --> rule_source_content_helm
    # TODO: detect Kustomize by presence of kustomization.yaml, kustomization.yml, or Kustomization --> rule_source_content_kustomize
    # TODO: default to plain Kubernetes resources otherwise --> rule_source_content_kubernetes
    return []


def rule_source_content_helm(document):
    # TODO: verify helm template into kubectl validation works
    return []


def rule_source_content_kustomize(document):
    # TODO: verify kustomize build into kubectl validation works
    return []


def rule_source_content_kubernetes(document):
    # TODO: verify kubectl validation works
    return []


top = [
    rule_metadata_finalizer,
    rule_destination_namespace,
    rule_destination_server,
    rule_project_exists,
    rule_source_repo_accessible,
]
