from kubernetes import client as k8s_client, config as k8s_config
import logging
import sys
logging.basicConfig(level=logging.INFO)

class KubernetesSecretConnector():

    def __init__(self):
        self.config        = k8s_config.load_incluster_config()
        self.secret_client = k8s_client.V1Secret()
        self.core_api      = k8s_client.CoreV1Api()

    def secret_list_by_ns(self):
        try:
            secrets = self.core_api.list_secret_for_all_namespaces(
                label_selector="created_by=credential_manager",
            ).items
        except Exception as e:
            raise e

        ret = {}
        for secret in secrets:
            ret[secret.metadata.namespace] = []

        for secret in secrets:
            ret[secret.metadata.namespace].append(secret.metadata.name)

        return ret

    def get(self, secret_name, namespace):
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

    def create(self, name, data, namespace = 'default', init = False):
        # define
        self.secret_client.metadata = k8s_client.V1ObjectMeta(
            name   = name,
            labels = data['labels']
        )
        self.secret_client.data = data['body']

        # apply
        try:
            if init:
                self.secret_client.type = "kubernetes.io/dockerconfigjson"
                self.core_api.create_namespaced_secret(namespace=namespace, body=self.secret_client)
                logging.info(f'{name} has been created successfully!')
            else:
                self.core_api.patch_namespaced_secret(name=name, namespace=namespace, body=self.secret_client)
                logging.info(f'{name} has been updated successfully!')
        except Exception as e:
            raise e

    def delete(self, name, namespace = 'default'):
        try:
            self.core_api.delete_namespaced_secret(name=name,namespace=namespace)
            logging.info(f'{name} has been deleted successfully!')
        except Exception as e:
            raise e