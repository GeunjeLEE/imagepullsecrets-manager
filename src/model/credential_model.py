from schematics import Model
from schematics.types import StringType, ModelType


class DockerhubCredentialModel(Model):
    docker_registry = StringType(required=True)
    docker_user = StringType(required=True)
    docker_password = StringType(required=True)
    docker_email = StringType(required=True)


class DockerhubModel(Model):
    name = StringType(required=True)
    kubernetes_namespace = StringType(required=True)
    type = StringType(required=True)
    credential = ModelType(DockerhubCredentialModel)


class EcrCredentialModel(Model):
    aws_access_key_id = StringType(required=True)
    aws_secret_access_key = StringType(required=True)
    aws_ecr_repository_region = StringType(required=True)


class EcrModel(Model):
    name = StringType(required=True)
    kubernetes_namespace = StringType(required=True)
    type = StringType(required=True)
    credential = ModelType(EcrCredentialModel)
