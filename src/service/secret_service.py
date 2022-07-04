from connector.kubernetes_secret_connector import KubernetesSecretConnector
from connector.ecr_connector import EcrConnector
import base64
import json
import logging
import sys
import time


class SecretService():
    def __init__(self):
        self.secret_config = None
        self.secret_connector = KubernetesSecretConnector()

    def set_config(self, secret_config):
        self.secret_config = secret_config
        self.repository_credential = self._generate_repository_credential(self.secret_config)

    def clean_up(self, config):
        actual_secret_list_by_ns = self.secret_connector.secret_list_by_ns()

        credential_by_ns = {}
        for credential in config:
            credential_by_ns[credential['kubernetes_namespace']] = []

        for credential in config:
            credential_by_ns[credential['kubernetes_namespace']].append(credential['name'])

        for namespace, _ in actual_secret_list_by_ns.items():
            for actual_name in actual_secret_list_by_ns[namespace]:
                if not credential_by_ns.get(namespace) or actual_name not in credential_by_ns[namespace]:
                    self.secret_connector.delete(actual_name,namespace)

    def run(self):
        if not self.secret_config:
            logging.error("No configuration set.")
            sys.exit(1)

        secret_name  = self.secret_config['name']
        kubernetes_namespace = self.secret_config['kubernetes_namespace']
        secret_data = {
            'labels': {
                'created_by': 'private_registry_secret_manager',
                'repo_type': self.secret_config['type'],
                'expire_date': str(self.repository_credential['token_expire_date'])
            },
            'body': {
                '.dockerconfigjson': self.repository_credential['dockerconfigjson']
            }
        }

        self._update_secret(secret_name, secret_data, kubernetes_namespace)

    def _update_secret(self, secret_name, secret_data, kubernetes_namespace):
        secret = self.secret_connector.get(secret_name, kubernetes_namespace)

        if not secret:
            self.secret_connector.create(secret_name, secret_data, kubernetes_namespace, init=True)
            return 0

        if secret.metadata.labels['repo_type'] == "DOCKER":
            if self._is_configuration_updated(secret):
                self.secret_connector.create(secret_name, secret_data, kubernetes_namespace, init=False)
        elif secret.metadata.labels['repo_type'] == "ECR":
            token_expiration = float(secret.metadata.labels['expire_date'])
            if self._is_token_expired(token_expiration):
                self.secret_connector.create(secret_name, secret_data, kubernetes_namespace, init=False)

    def _generate_repository_credential(self, secret_config):
        credential = {}
        if secret_config['type'] == 'ECR':
            ecr_authorization_token = self._get_ecr_authorization_token(secret_config['credential'])

            credential['token_expire_date'] = time.mktime(ecr_authorization_token['token_expire_date'].timetuple()) # convert to unix time
            user, password = self._data_b64decode(ecr_authorization_token['server']).split(':')  ## server key has token...
            server = ecr_authorization_token['token']  ## token key has repository url...
            email = 'service@cloudforet.io'


        elif secret_config['type'] == 'DOCKER':
            credential['token_expire_date'] = None
            user = secret_config['credential']['docker_user']
            password = secret_config['credential']['docker_password']
            server = secret_config['credential']['docker_registry']
            email = secret_config['credential']['docker_email']

        else:
            logging.error("type error")
            sys.exit(1)

        credential['dockerconfigjson'] = self._generate_dockerjson(server, user, password, email)

        return credential

    def _generate_dockerjson(self, url, username, password, email):
        auth = self._data_b64encode(f'{username}:{password}')

        row_data = {
            "auths": {
                    url: {
                        "username": username,
                        "password": password,
                        "email": email,
                        "auth": auth
                    }
            }
        }

        return base64.b64encode(json.dumps(row_data).encode()).decode()

    def _is_configuration_updated(self, secret):
        secret_json = secret.data['.dockerconfigjson']
        config_json = self.repository_credential['dockerconfigjson']

        if secret_json != config_json:
            return True

        return False

    @staticmethod
    def _get_ecr_authorization_token(aws_credential):
        ecr = EcrConnector(aws_credential)
        authorization = ecr.get_authorization_token()

        if not authorization:
            return 1

        return {
            'server': authorization['authorizationData'][0]['authorizationToken'],
            'token': authorization['authorizationData'][0]['proxyEndpoint'],
            'token_expire_date': authorization['authorizationData'][0]['expiresAt']
        }

    @staticmethod
    def _is_token_expired(token_expiration_float):
        if not token_expiration_float:
            return False

        current = time.time()
        if current >= token_expiration_float:
            return True

        return False

    @staticmethod
    def _data_b64encode(input_str):
        input_ascii = input_str.encode("ascii")
        return base64.b64encode(input_ascii).decode("utf-8")

    @staticmethod
    def _data_b64decode(encoded):
        return base64.b64decode(encoded).decode('UTF-8')
