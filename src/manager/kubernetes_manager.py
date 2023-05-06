from connector.kubernetes_connector import KubernetesConnector

import logging
import time


class KubernetesManager:
    def __init__(self):
        self.kubernetes_connector = KubernetesConnector()
        self.created_by = 'imagepullsecrets-manager'

    def scan_secret(self, credential):
        secret_name = credential['name']
        kubernetes_namespace = credential['kubernetes_namespace']
        secret_manifest = {
            'labels': {
                'created_by': self.created_by,
                'repo_type': credential['type'],
                'token_expiration_date': str(credential['token_expiration_date'])
            },
            'body': {
                '.dockerconfigjson': credential['dockerconfigjson']
            }
        }
        actual_secret = self.kubernetes_connector.get_secret(secret_name, kubernetes_namespace)

        if not actual_secret:
            self.kubernetes_connector.create_secret(secret_name, secret_manifest, kubernetes_namespace)
            return True

        if not self._is_managed_secret(actual_secret):
            logging.warning(f'secret({secret_name}) already exist but not managed by imagepullsecret-manager. '
                            f'it will be skipped.')
            return False

        if actual_secret.metadata.labels['repo_type'] == "DOCKER":
            if self._is_docker_login_changed(actual_secret, secret_manifest):
                self.kubernetes_connector.patch_secret(secret_name, secret_manifest, kubernetes_namespace)
        elif actual_secret.metadata.labels['repo_type'] == "ECR":
            token_expiration_date = float(actual_secret.metadata.labels['token_expiration_date'])
            if self._is_ecr_token_expired(token_expiration_date):
                self.kubernetes_connector.patch_secret(secret_name, secret_manifest, kubernetes_namespace)

        return True

    def cleanup_secret(self, secret_credential_by_ns):
        actual_secret_list_by_ns = self.kubernetes_connector.list_managed_secrets_by_namespace(label=self.created_by)

        for namespace, _ in actual_secret_list_by_ns.items():
            for actual_secret_name in actual_secret_list_by_ns[namespace]:
                is_delete = False
                
                secrets = secret_credential_by_ns.get(namespace)
                if not secrets or actual_secret_name not in secret_credential_by_ns[namespace]:
                    is_delete = True

                if is_delete:
                    logging.info(f'Found a deprecated secret({actual_secret_name})')
                    self.kubernetes_connector.delete_secret(actual_secret_name, namespace)

    @staticmethod
    def _is_docker_login_changed(k8s_secret, secret_data):
        dockerconfigjson_in_k8s_secret = k8s_secret.data['.dockerconfigjson']
        config_json = secret_data['body']['.dockerconfigjson']

        if dockerconfigjson_in_k8s_secret != config_json:
            return True

        return False

    @staticmethod
    def _is_ecr_token_expired(token_expiration_date):
        if not token_expiration_date:
            return False

        current = time.time()
        # 10 minutes before expiration
        if current >= token_expiration_date - 600:
            return True

        return False

    @staticmethod
    def _is_managed_secret(secret):
        secret_name = secret.metadata.__dict__.get('_name')
        labels = secret.metadata.labels

        if not labels.get('created_by') or labels['created_by'] != "imagepullsecrets-manager":
            logging.warning(
                f"{secret_name} is might not a secret managed by imagepullsecrets-model")
            logging.warning('skip update processing')
            return False

        return True
