#!/usr/bin/env python3

import sys
import ruamel.yaml
import rules


def log_info(document_source, document_source_index, message):
    print("[info] [{}@{}]: {}".format(document_source, document_source_index, message))


def log_error(document_source, document_source_index, message):
    print("[error] [{}@{}]: {}".format(document_source, document_source_index, message))


def log_warning(document_source, document_source_index, message):
    print("[warning] [{}@{}]: {}".format(document_source, document_source_index, message))


def lint_document(document_source, document_source_index, document):
    if "apiVersion" not in document:
        log_info(document_source, document_source_index, "document not recognized as an ArgoCD Application")
        return
    if document["apiVersion"] != "argoproj.io/v1alpha1":
        log_info(document_source, document_source_index, "document not recognized as an ArgoCD Application")
        return
    if "kind" not in document:
        log_info(document_source, document_source_index, "document not recognized as an ArgoCD Application")
        return
    if document["kind"] != "Application":
        log_info(document_source, document_source_index, "document not recognized as an ArgoCD Application")
        return
    log_info(document_source, document_source_index, "document is an ArgoCD Application")
    queue = []
    queue.extend(rules.top)
    while len(queue) > 0:
        rule = queue.pop()
        try:
            log_info(document_source, document_source_index, "running rule {}".format(rule.__name__))
            continuations = rule(document)
            queue = continuations + queue
        except Exception as e:
            log_error(document_source, document_source_index, "failed rule {}: {}".format(rule.__name__, e))


def lint_file(yaml_source):
    yaml_stream = sys.stdin if yaml_source == '-' else open(yaml_source)
    with yaml_stream:
        documents = ruamel.yaml.load_all(yaml_stream, Loader=ruamel.yaml.RoundTripLoader)
        for document_index, document in enumerate(documents):
            lint_document(yaml_source, document_index, document)


def main():
    for yaml_source in sys.argv[1:]:
        lint_file(yaml_source)


if __name__ == '__main__':
    main()
