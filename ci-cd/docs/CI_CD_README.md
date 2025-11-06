# CI/CD Integration Guide

This document provides comprehensive guidance for integrating the Dynamic Analysis Agent into various CI/CD platforms for automated security scanning.

## Table of Contents

- [GitHub Actions](#github-actions)
- [GitLab CI/CD](#gitlab-cicd)
- [Jenkins](#jenkins)
- [Azure DevOps](#azure-devops)
- [CircleCI](#circleci)
- [Travis CI](#travis-ci)
- [Bitbucket Pipelines](#bitbucket-pipelines)
- [Docker Integration](#docker-integration)
- [Kubernetes Integration](#kubernetes-integration)
- [Helm Charts](#helm-charts)
- [ArgoCD Integration](#argocd-integration)

## GitHub Actions

The security scan workflow (`.github/workflows/security-scan.yml`) provides automated security scanning with the following features:

### Features
- Triggers on push/PR to main/develop branches
- Scheduled nightly scans
- Manual workflow dispatch with custom parameters
- Docker-based scanning
- Result artifact upload
- Build failure on critical vulnerabilities

### Usage

The workflow will automatically run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger via GitHub Actions UI
- Scheduled runs (daily at 2 AM UTC)

### Parameters
- `target_image`: Docker image to scan (default: `nginx:latest`)
- `ports`: Ports to scan (default: `80`)
- `fail_on_critical`: Fail build on critical vulnerabilities (default: `true`)

### Example Manual Trigger
```yaml
# Via GitHub Actions UI or API
target_image: myapp:latest
ports: 8080,8443
fail_on_critical: true
```

## GitLab CI/CD

The GitLab CI configuration (`.gitlab-ci.yml`) includes multiple stages and jobs:

### Pipeline Stages
1. **build**: Build the scanner image
2. **security_scan**: Run security scans
3. **Quality Gate**: Optional security threshold checking
4. **deploy**: Deploy reports to GitLab Pages

### Features
- Multi-target scanning support
- Artifact storage with 30-day retention
- JUnit test reporting
- Security gate with configurable thresholds
- Scheduled nightly scans

### Environment Variables
```bash
TARGET_IMAGE=nginx:latest          # Image to scan
TARGET_PORTS=80,443               # Ports to scan
CI_APPLICATION_TAG=v1.0.0         # For application scanning
```

### Security Gates
The pipeline includes optional security gates that can fail builds based on vulnerability counts:
- Critical vulnerabilities always fail
- High vulnerabilities can be configured to fail
- Configurable via environment variables

## Jenkins

The Jenkins pipeline (`Jenkinsfile`) provides:

### Features
- Parameterized builds
- Multi-format output support (JSON/HTML/PDF/CSV)
- JUnit test reporting for Jenkins UI
- Build status updates with vulnerability summaries
- Post-build actions and notifications

### Pipeline Parameters
- `TARGET_IMAGE`: Docker image to scan
- `TARGET_PORTS`: Comma-separated ports
- `OUTPUT_FORMAT`: json, html, pdf, csv
- `FAIL_ON_CRITICAL`: Boolean
- `FAIL_ON_HIGH`: Boolean

### Setup Instructions
1. Install Docker plugin in Jenkins
2. Configure Docker access for the Jenkins agent
3. Create a new pipeline job using the `Jenkinsfile`
4. Configure build parameters as needed

## Azure DevOps

The Azure DevOps pipeline (`azure-pipelines.yml`) supports:

### Features
- Multi-stage pipelines
- Matrix builds for multiple targets
- Artifact publishing
- Build validation and quality gates
- Scheduled builds

### Pipeline Structure
- **Build**: Create scanner image
- **SecurityScan**: Execute security scans
- **QualityGate**: Validate security thresholds
- **MultiTargetScan**: Scan multiple applications

### Variables
```yaml
scannerImageTag: 'dynamic-analysis-agent:$(Build.BuildId)'
scanResultsDir: 'results'
targetImage: 'nginx:latest'
targetPorts: '80'
outputFormat: 'json'
failOnCritical: true
failOnHigh: false
```

## CircleCI

The CircleCI configuration (`.circleci/config.yml`) includes:

### Features
- Reusable commands and executors
- Orb-based architecture
- Parameterized workflows
- Scheduled nightly scans
- Comprehensive reporting

### Workflows
- **security_scan**: Standard security scanning
- **nightly_scan**: Automated nightly scans

### Parameters
- `target_image`: Image to scan
- `target_ports`: Ports to scan
- `output_format`: Output format
- `fail_on_critical`: Fail on critical vulns
- `fail_on_high`: Fail on high vulns

## Travis CI

The Travis CI configuration (`.travis.yml`) provides:

### Features
- Matrix builds for multiple targets
- Parallel execution
- Build caching
- Notifications (email, Slack, webhooks)
- Cron scheduling

### Build Matrix
```yaml
env:
  - TARGET_IMAGE=nginx:latest TARGET_PORTS=80
  - TARGET_IMAGE=httpd:latest TARGET_PORTS=80
  - TARGET_IMAGE=redis:latest TARGET_PORTS=6379
```

### Notifications
Configure notifications in `.travis.yml`:
```yaml
notifications:
  slack:
    rooms:
      - yourcompany:yourtoken#security-scans
    on_success: change
    on_failure: always
```

## Bitbucket Pipelines

The Bitbucket configuration (`bitbucket-pipelines.yml`) supports:

### Pipeline Types
- **default**: Standard CI pipeline
- **branches**: Branch-specific configurations
- **pull-requests**: PR validation
- **custom**: Scheduled/manual pipelines

### Features
- Multi-target scanning
- Artifact storage
- Branch-specific logic
- Scheduled pipelines (Premium feature)

## Docker Integration

### CI-Optimized Image

Use `Dockerfile.ci` for faster CI builds:

```bash
# Build CI-optimized image
docker build -f Dockerfile.ci -t scanner-ci:latest .

# Run scan
docker run --rm \
  -v $(pwd)/results:/app/results \
  scanner-ci:latest \
  python main.py --image nginx:latest --port 80
```

### Docker Compose for Local Testing

```yaml
version: '3.8'
services:
  scanner:
    build:
      context: .
      dockerfile: Dockerfile.ci
    volumes:
      - ./results:/app/results
    command: python main.py --image nginx:latest --port 80 --api
```

## Kubernetes Integration

### Deployment

Deploy using the provided manifests:

```bash
# Create namespace
kubectl create namespace security

# Apply manifests
kubectl apply -f k8s/deployment.yaml

# Check deployment
kubectl get pods -n security
```

### Configuration

Customize the deployment via ConfigMap:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scanner-config
data:
  config.yaml: |
    docker:
      default_port: 8080
    scanning:
      timeout: 600
```

### Scaling

Scale the deployment:
```bash
kubectl scale deployment dynamic-analysis-agent --replicas=3 -n security
```

## Helm Charts

### Installation

```bash
# Add repository (if published)
helm repo add security https://charts.yourcompany.com
helm repo update

# Install chart
helm install security-scanner ./helm/dynamic-analysis-agent \
  --namespace security \
  --create-namespace \
  --set scanConfig.targetImage=myapp:latest \
  --set scanConfig.targetPorts="8080,8443"
```

### Configuration

Key values to customize:
```yaml
# values.yaml
scanConfig:
  targetImage: "myapp:latest"
  targetPorts: "8080,8443"
  outputFormat: "json"
  failOnCritical: true

resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"

persistence:
  enabled: true
  size: 20Gi
```

### Upgrading

```bash
helm upgrade security-scanner ./helm/dynamic-analysis-agent \
  --namespace security \
  --set image.tag=v2.0.0
```

## ArgoCD Integration

### Application Deployment

```bash
# Apply ArgoCD application
kubectl apply -f argocd/application.yaml

# Check application status
kubectl get applications -n argocd
```

### GitOps Workflow

1. Update Helm values in Git
2. ArgoCD detects changes
3. Automatically syncs to cluster
4. Validates deployment health

### Configuration

Customize ArgoCD application:
```yaml
spec:
  source:
    helm:
      parameters:
        - name: scanConfig.targetImage
          value: myapp:latest
        - name: scanConfig.targetPorts
          value: "8080,8443"
```

## Best Practices

### 1. Security Gates
- Always fail builds on critical vulnerabilities
- Consider failing on high vulnerabilities for production
- Use different thresholds for different branches

### 2. Scheduling
- Run scans on every commit for fast feedback
- Schedule comprehensive scans nightly
- Use different scan depths for different triggers

### 3. Reporting
- Store scan results as artifacts
- Generate human-readable reports
- Integrate with security dashboards

### 4. Performance
- Use CI-optimized Docker images
- Cache dependencies and layers
- Run scans in parallel when possible

### 5. Monitoring
- Monitor scan execution times
- Track vulnerability trends
- Set up alerts for scan failures

## Troubleshooting

### Common Issues

1. **Docker permission denied**
   ```bash
   # Add user to docker group or use sudo
   sudo usermod -aG docker $USER
   ```

2. **Port conflicts**
   ```bash
   # Use different ports or --network host
   docker run --network host ...
   ```

3. **Memory issues**
   ```bash
   # Increase memory limits
   resources:
     limits:
       memory: 4Gi
   ```

4. **Scan timeouts**
   ```bash
   # Increase timeout values
   scanning:
     timeout: 1200
   ```

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py --image target --port 80
```

### Support

For issues specific to CI/CD integration:
1. Check CI platform logs
2. Verify Docker configuration
3. Test locally with Docker
4. Review security scan results

---

## Quick Start Examples

### GitHub Actions
```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t scanner .
      - run: docker run -v $(pwd)/results:/results scanner --image nginx:latest
```

### GitLab CI
```yaml
security_scan:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t scanner .
    - docker run -v $(pwd)/results:/results scanner --image $TARGET_IMAGE
  artifacts:
    paths:
      - results/
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                sh 'docker build -t scanner .'
                sh 'docker run -v $(pwd)/results:/results scanner --image nginx:latest'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'results/**'
        }
    }
}
```

This guide covers the complete CI/CD integration setup. Choose the platform that best fits your infrastructure and follow the specific configuration examples provided.
