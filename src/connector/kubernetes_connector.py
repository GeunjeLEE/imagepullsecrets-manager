from kubernetes.client import exceptions as k8s_exceptions
from kubernetes import client as k8s_client, config as k8s_config
import logging
logging.basicConfig(level=logging.INFO)


class KubernetesConnector:
    def __init__(self):
        self.config = k8s_config.load_kube_config()
        self.core_api = k8s_client.CoreV1Api()
        self.secret_client = k8s_client.V1Secret()

    def list_managed_secrets_by_namespace(self, label):
        try:
            secrets = self.core_api.list_secret_for_all_namespaces(
                label_selector=f"created_by={label}",
            ).items
        except Exception as e:
            raise e

        ret = {}
        for secret in secrets:
            ret[secret.metadata.namespace] = []

        for secret in secrets:
            ret[secret.metadata.namespace].append(secret.metadata.name)

        return ret

    def get_secret(self, secret_name, namespace):
        try:
            return self.core_api.read_namespaced_secret(secret_name, namespace)
        except k8s_client.exceptions.ApiException as e:
            if e.status == 404:
                logging.warning(f'secret({secret_name}) not found, it will be created.')
                return False
            else:
                raise e
        except Exception as e:
            raise e

    def create_secret(self, name, manifest, namespace='default'):
        # define
        self.secret_client.metadata = k8s_client.V1ObjectMeta(
            name=name,
            labels=manifest['labels']
        )
        self.secret_client.data = manifest['body']

        # apply
        try:
            logging.info(f'Creating {name}...')
            self.secret_client.type = "kubernetes.io/dockerconfigjson"
            self.core_api.create_namespaced_secret(namespace=namespace, body=self.secret_client)
        except k8s_exceptions.ApiException as e:
            logging.error(f'({e.status}){e.body}')
        except Exception as e:
            raise e

    def patch_secret(self, name, manifest, namespace='default'):
        # define
        self.secret_client.metadata = k8s_client.V1ObjectMeta(
            name=name,
            labels=manifest['labels']
        )
        self.secret_client.data = manifest['body']

        # apply
        try:
            logging.info(f'Patching {name}...')
            self.core_api.patch_namespaced_secret(name=name, namespace=namespace, body=self.secret_client)
        except k8s_exceptions.ApiException as e:
            logging.error(f'({e.status}){e.body}')
        except Exception as e:
            raise e

    def delete_secret(self, name, namespace='default'):
        try:
            logging.info(f'Deleting {name}...')
            self.core_api.delete_namespaced_secret(name=name,namespace=namespace)
        except Exception as e:
            raise e
