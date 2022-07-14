from connector.kubernetes_secret_connector import KubernetesSecretConnector
from connector.ecr_connector import EcrConnector
import base64
import json
import logging
import time


class SecretService:
    def __init__(self, raw_credentials):
        self.secret_connector = KubernetesSecretConnector()
        self.credentials = self._set(raw_credentials)

    def run(self):
        for credential in self.credentials:
            secret_name = credential['name']
            kubernetes_namespace = credential['kubernetes_namespace']
            secret_data = {
                'labels': {
                    'created_by': 'imagepullsecrets-manager',
                    'repo_type': credential['type'],
                    'token_expiration_date': str(credential['token_expiration_date'])
                },
                'body': {
                    '.dockerconfigjson': credential['dockerconfigjson']
                }
            }

            self._update_secret(secret_name, secret_data, kubernetes_namespace)

    def clean_up(self):
        credential_by_ns = {}
        for credential in self.credentials:
            credential_by_ns[credential['kubernetes_namespace']] = []

        for credential in self.credentials:
            credential_by_ns[credential['kubernetes_namespace']].append(credential['name'])

        actual_secret_list_by_ns = self.secret_connector.secret_list_by_ns()
        for namespace, _ in actual_secret_list_by_ns.items():
            for actual_secret_name in actual_secret_list_by_ns[namespace]:
                if not credential_by_ns.get(namespace) or actual_secret_name not in credential_by_ns[namespace]:
                    self.secret_connector.delete(actual_secret_name, namespace)

    def _set(self, credentials):
        results = []
        for credential in credentials:
            results.append(self._get_additional_data(credential))

        return results

    def _get_additional_data(self, raw_credential):
        credential = raw_credential
        if raw_credential['type'] == 'ECR':
            ecr_authorization_token = self._get_ecr_authorization_token(raw_credential['credential'])
            # convert to unix time
            credential['token_expiration_date'] = time.mktime(ecr_authorization_token['token_expiration_date'].timetuple())

            # server key has token...
            user, password = self._data_b64decode(ecr_authorization_token['server']).split(':')
            # token key has repository url...
            server = ecr_authorization_token['token']
            email = 'service@cloudforet.io'

        elif raw_credential['type'] == 'DOCKER':
            credential['token_expiration_date'] = None

            user = raw_credential['credential']['docker_user']
            password = raw_credential['credential']['docker_password']
            server = raw_credential['credential']['docker_registry']
            email = raw_credential['credential']['docker_email']

        credential['dockerconfigjson'] = self._generate_dockerjson(server, user, password, email)

        return credential

    def _update_secret(self, secret_name, secret_data, kubernetes_namespace):
        target_secret = self.secret_connector.get(secret_name, kubernetes_namespace)

        if not target_secret:
            self.secret_connector.create(secret_name, secret_data, kubernetes_namespace, init=True)
            return False

        if not self._is_managed_secret(target_secret):
            return False

        if target_secret.metadata.labels['repo_type'] == "DOCKER":
            if self._is_configuration_updated(target_secret, secret_data):
                self.secret_connector.create(secret_name, secret_data, kubernetes_namespace, init=False)
        elif target_secret.metadata.labels['repo_type'] == "ECR":
            token_expiration_date = float(target_secret.metadata.labels['token_expiration_date'])
            if self._is_token_expired(token_expiration_date):
                self.secret_connector.create(secret_name, secret_data, kubernetes_namespace, init=False)

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

    @staticmethod
    def _is_configuration_updated(k8s_secret, secret_data):
        dockerconfigjson_in_k8s_secret = k8s_secret.data['.dockerconfigjson']
        config_json = secret_data['body']['.dockerconfigjson']

        if dockerconfigjson_in_k8s_secret != config_json:
            return True

        return False

    @staticmethod
    def _get_ecr_authorization_token(aws_credential):
        ecr = EcrConnector(aws_credential)
        authorization = ecr.get_authorization_token()

        return {
            'server': authorization['authorizationData'][0]['authorizationToken'],
            'token': authorization['authorizationData'][0]['proxyEndpoint'],
            'token_expiration_date': authorization['authorizationData'][0]['expiresAt']
        }

    @staticmethod
    def _is_managed_secret(secret: object):
        if not secret.metadata.__dict__.get('_labels'):
            logging.warning(f"{secret.metadata.__dict__.get('_name')} has no labels. may be not a secret managed by imagepullsecrets-manager")
            logging.warning('skip update processing')
            return False

        if not secret.metadata.labels.get('created_by') or secret.metadata.labels['created_by'] != "imagepullsecrets-manager":
            logging.warning(f"{secret.metadata.__dict__.get('_name')} is not a secret managed by imagepullsecrets-manager")
            logging.warning('skip update processing')
            return False

        return True

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
