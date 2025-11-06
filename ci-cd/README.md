# CI/CD Integration

This directory contains comprehensive CI/CD integration configurations for the Dynamic Analysis Agent across all major platforms.

## Directory Structure

```
ci-cd/
├── github/                 # GitHub Actions workflows
│   └── security-scan.yml
├── gitlab/                 # GitLab CI/CD configuration
│   └── .gitlab-ci.yml
├── jenkins/                # Jenkins pipeline configuration
│   └── Jenkinsfile
├── azure/                  # Azure DevOps pipelines
│   └── azure-pipelines.yml
├── circleci/               # CircleCI configuration
│   └── config.yml
├── travis/                 # Travis CI configuration
│   └── .travis.yml
├── bitbucket/              # Bitbucket Pipelines configuration
│   └── bitbucket-pipelines.yml
├── docker/                 # CI-optimized Docker images
│   └── Dockerfile.ci
├── kubernetes/             # Kubernetes deployment manifests
│   └── deployment.yaml
├── helm/                   # Helm charts for Kubernetes deployment
│   └── dynamic-analysis-agent/
├── argocd/                 # ArgoCD GitOps configuration
│   └── application.yaml
└── docs/                   # Documentation
    └── CI_CD_README.md
```

## Quick Start

### Choose Your CI/CD Platform

1. **GitHub Actions**: Copy `github/security-scan.yml` to `.github/workflows/`
2. **GitLab CI**: Copy `gitlab/.gitlab-ci.yml` to your repository root
3. **Jenkins**: Copy `jenkins/Jenkinsfile` to your repository root
4. **Azure DevOps**: Copy `azure/azure-pipelines.yml` to your repository root
5. **CircleCI**: Copy `circleci/config.yml` to `.circleci/`
6. **Travis CI**: Copy `travis/.travis.yml` to your repository root
7. **Bitbucket**: Copy `bitbucket/bitbucket-pipelines.yml` to your repository root

### Docker Deployment

For Kubernetes/Helm deployment:
```bash
# Using Kubernetes manifests
kubectl apply -f kubernetes/

# Using Helm charts
helm install security-scanner helm/dynamic-analysis-agent/

# Using ArgoCD
kubectl apply -f argocd/
```

## Configuration

Each platform supports environment variables for customization:

- `TARGET_IMAGE`: Docker image to scan (default: nginx:latest)
- `TARGET_PORTS`: Ports to scan (default: 80)
- `OUTPUT_FORMAT`: json, html, pdf, csv (default: json)
- `FAIL_ON_CRITICAL`: Fail build on critical vulnerabilities (default: true)
- `FAIL_ON_HIGH`: Fail build on high vulnerabilities (default: false)

## Documentation

For detailed setup instructions, see [CI/CD Integration Guide](docs/CI_CD_README.md).

## Features

- ✅ Automated security scanning on commits/PRs/schedules
- ✅ Multi-format reporting (JSON/HTML/PDF/CSV)
- ✅ Configurable security gates
- ✅ Artifact storage and build integration
- ✅ Multi-target scanning support
- ✅ Production deployment options
- ✅ Platform-specific optimizations

## Support

All major CI/CD platforms are supported with consistent interfaces and comprehensive security scanning capabilities.
