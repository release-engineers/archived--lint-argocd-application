#!/usr/bin/env python3

import sys
import ruamel.yaml


def lint_document(document_source_path, document_source_index, document):
    print("# document: {}[{}]".format(document_source_path, document_source_index))
    pass


def lint_file(yaml_file_path):
    yaml_stream = sys.stdin if yaml_file_path == '-' else open(yaml_file_path)
    with yaml_stream:
        documents = ruamel.yaml.load_all(yaml_stream, Loader=ruamel.yaml.RoundTripLoader)
        for document_index, document in enumerate(documents):
            lint_document(yaml_file_path, document_index, document)


def main():
    for yaml_file_path in sys.argv[1:]:
        lint_file(yaml_file_path)


if __name__ == '__main__':
    main()
