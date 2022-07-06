# imagePullSecrets-manager
Create and manage `secrets` to pull images from private registry (ECR or Docker Hub) for kubernetes pod

imagePullSecrets-manager works as [a kubernetes cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) and easily creates and manages secrets to use as 'imagePullSecrets'.

---

### What's imagePullSecrets?
To pull images from a private registry, you must authenticate to that registry.

There are several ways to authenticate the registry, you can use [imagePullSecrets]((https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#registry-secret-existing-credentials)) among them.

---

### How imagePullSecrets is managed

By default, if there is no `imagePullSecrets`, it will be created

if there is `imagePullSecrets`, it will be updated differently depending on the type.<br>
(imagePullSecrets-manager manages only `secret` created by itself.)
- ECR
  - If the ECR token expires, update token and replace `imagePullSecrets`.
- DOCKER
  - If the secret configuration is updated, replace `imagePullSecrets`.

also, if there is `imagePullSecrets` that does not exist in 'config', it will be deleted

## How to use?
imagePullSecrets-manager is deployed using helm.
### 1. configure

Edit the helm value(default or create custom value) to manage imagePullSecrets-manager.

in `config`.`secrets` section, add repository credential required to create imagePullSecrets.

> If you don't know imagePullSecrets, see the documentation.<br>
> https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/

```yaml
name: imagePullSecrets-manager
namespace: default
image:
    name: nigasa12/imagepullsecrets-manager
    version: <image-version>
imagePullPolicy: IfNotPresent
job_schedule: "* * * * *" # every minute
successfulJobsHistoryLimit: 10
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

### deploy

- using default value
```bash
helm install imagePullSecrets-manager ./helm
```
- using custom value
```bash
vim {path}/values.yaml
helm install imagePullSecrets-manager -f values.yaml /{path}/helm
```

### update

```
helm upgrade imagePullSecrets-manager {-f values.yaml} ./helm
```
