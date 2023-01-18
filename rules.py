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
    # verify namespace exists
    return []


def rule_destination_server(document):
    if "spec" not in document:
        raise Exception("missing .spec")
    if "destination" not in document["spec"]:
        raise Exception("missing .spec.destination")
    if "server" not in document["spec"]["destination"]:
        raise Exception("missing .spec.destination.server")
    # verify server exists
    return []


def rule_project_exists(document):
    if "spec" not in document:
        raise Exception("missing .spec")
    if "project" not in document["spec"]:
        raise Exception("missing .spec.project")
    # verify project exists
    return [rule_project_exists_and_namespace_allowed, rule_project_exists_and_server_allowed]


def rule_project_exists_and_namespace_allowed(document):
    project = document["spec"]["project"]
    # verify project allows for deployment into .spec.destination.namespace
    return []


def rule_project_exists_and_server_allowed(document):
    project = document["spec"]["project"]
    # verify project allows for deployment into .spec.destination.server
    return []


def rule_source_repo_accessible(document):
    if "spec" not in document:
        raise Exception("missing .spec")
    if "source" not in document["spec"]:
        raise Exception("missing .spec.source")
    if "repoURL" not in document["spec"]["source"]:
        raise Exception("missing .spec.source.repoURL")
    # verify repoURL accessible
    return [rule_source_repo_accessible_revision]


def rule_source_repo_accessible_revision(document):
    source = document["spec"]["source"]
    if "targetRevision" not in source:
        raise Exception("missing .spec.source.targetRevision")
    # verify targetRevision exists in repository
    return [rule_source_repo_accessible_revision_and_path]


def rule_source_repo_accessible_revision_and_path(document):
    source = document["spec"]["source"]
    if "path" not in source:
        raise Exception("missing .spec.source.path")
    # verify path exists in repository at targetRevision
    return []


top = [
    rule_metadata_finalizer,
    rule_destination_namespace,
    rule_destination_server,
    rule_project_exists,
    rule_source_repo_accessible,
]
