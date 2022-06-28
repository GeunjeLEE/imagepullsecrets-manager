# private-registry-secret-manager(a.k.a prs-manager)
Create and manage `Private Registry Secret` to pull images from private registry (ECR or Docker Hub) for kubernetes pod

prs-manager works as [a kubernetes cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) and easily creates and manages `Private Registry Secrets`.

### What's the Private Registry Secret?
To pull images from a private registry, you must authenticate to that registry.

There are several ways to authenticate the registry,<br>
but [You can authenticate using a kubernetes secret type of type dockerconfigjson.](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#registry-secret-existing-credentials)

prs-manager calls it `Private Registry Secret`.

### How 'Private Registry Secret' is managed

By default, if there is no `private registry secret`, it will be created

if there is `personal registration secret`, it will be updated differently depending on the type.<br>
(prs-manager manages only `secret` created by itself.)
- ECR
  - If the ECR token expires, update token and replace `personal registration secrets`.
- DOCKER
  - If the secret configuration is updated, replace `personal registration secrets`.

also, if there is `personal registration secrets` that does not exist in 'secret configuration', it will be deleted

## Configuration

Edit the helm value(default or create custom value) to manage `Private Registry Secret`.

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
