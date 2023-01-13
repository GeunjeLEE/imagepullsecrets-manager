# imagepullsecrets-manager
Create and manage `secrets` to pull images from private registry (ECR or Docker Hub) for kubernetes pod

imagepullsecrets-manager works as [a kubernetes cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) and easily creates and manages secrets to use as `imagePullSecrets`.

---

### What's imagePullSecrets?
To pull images from a private registry, you must authenticate to that registry.

There are several ways to authenticate the registry, you can use [imagePullSecrets](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#registry-secret-existing-credentials) among them.

---

### How imagePullSecrets are managed
![스크린샷 2023-01-13 오전 10 43 11](https://user-images.githubusercontent.com/19552819/212217761-0f9d8ff3-300d-4621-9902-2e22928edf0c.png)

By default, `imagePullSecrets` are created if they don't exist.

if there are `imagePullSecrets`, They will be updated differently depending on the type.<br>
(imagepullsecrets-manager manages only `secret` created by itself.)
- ECR
  - If the ECR token expires, update token and update `imagePullSecrets`.
- DOCKER
  - If the secret configuration is updated, update `imagePullSecrets`.

Also, `imagePullSecrets` are deleted when they are deleted from configuration.

## Prerequisite
- kubectl
- helm

## How to use?
imagepullsecrets-manager are deployed using helm.<br>
imagepullsecrets-manager automatically creates and manages secrets by referring to the `config(in helm value)`.

### 1. configure

Edit the helm value(default or create custom value) to config imagepullsecrets-manager.

in `config`.`secrets` section, add repository credential required to create imagePullSecrets.

> If you don't know imagePullSecrets, see the documentation.<br>
> https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/

```yaml
name: imagepullsecrets-manager
namespace: default
image:
    name: nigasa12/imagepullsecrets-manager
    version: <image-version>
imagePullPolicy: IfNotPresent
job_schedule: "* * * * *" # every minute
successfulJobsHistoryLimit: 10
config:
  credentials:
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
helm install imagepullsecrets-manager ./helm
```
- using custom value
```bash
vim {path}/values.yaml
helm install imagepullsecrets-manager -f values.yaml /{path}/helm
```

### update

```
helm upgrade imagepullsecrets-manager {-f values.yaml} ./helm
```
