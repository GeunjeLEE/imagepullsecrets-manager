# prs-manager
Create and manage `Private Registry Secret` to pull images from private registry (ECR or Docker Hub)

prs-manager works as [a kubernetes cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) and easily creates and manages `Private Registry Secrets`.

## What's the Private Registry Secret?
To pull images from a private registry, you must authenticate to that registry.

There are several ways to authenticate the registry,<br>
but [You can authenticate using a kubernetes secret type of type dockerconfigjson.](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#registry-secret-existing-credentials)

prs-manager calls it `Private Registry Secret.`

## Configuration

Edit the helm value(default or create custom value) to manage `Private Registry Secret.`<br>

```yaml
name: prs-manager
namespace: default
image:
    name: nigasa12/prs-manager
    version: "0.1"
imagePullPolicy: IfNotPresent
job_schedule: "0 * * * *"
config:
  secrets:
    - name: ecr-dev
      kubernetes_namespace: default
      type: ECR
      credential:
        aws_access_key_id: foobargem
        aws_secret_access_key: foobargem
        aws_ecr_repository_region: ap-northeast-2
    - name: docker-example
      kubernetes_namespace: default
      type: DOCKER
      credential:
        docker_registry: docker.io
        docker_user: foobargem
        docker_password: password
        docker_email: foobargem@example.com
```

## Deployment

`psr-manager` is deployed using the local helm chart.

- using default value
```bash
helm install prs-manager ./helm
```
- using custom value
```bash
vim values.yaml
helm install prs-manager -f values.yaml ./helm
```