# lint-argocd-application

ArgoCD Application linter

## Development

### Prerequisites

- Python 3
- Kubectl
- Helm 3
- Kustomize

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Usage

```bash
./regenerate-yamls.sh
./lint.py build/*.yaml
```
