# lint-argocd-application

[![Status: Alpha](https://img.shields.io/badge/status-alpha-red)](https://release-engineers.com/open-source-badges/)

Lints ArgoCD Applications, going so far as to run actual (dry-run) kubectl commands and git clone-s to validate the application.

This solution runs tools such as Git, Kubectl, Helm, Kustomize, etc. Ensure that git is authorized to clone your repositories, and that kubectl is
authorized to run apply dry-runs against your cluster. It is not recommended to run this tool against Application manifests that are not under your
control.

## Usage

Invoke like so using your favorite shell;

```shell
./lint.py your-application.yaml [your-application.yaml ...]
```

Alternatively you can also use "-" to read from stdin like so;

```shell
cat your-application.yaml | ./lint.py -
```

### Prerequisites

- Python 3
- Git
- Kubectl
- Helm 3 (only for Helm-based applications)
- Kustomize (only for Kustomize-based applications)

## Development

### Prerequisites

- Python 3
- Git
- Kubectl
- Helm 3
- Kustomize

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Usage

```bash
./regenerate-yamls.sh
./lint.py build/*.yaml
```
