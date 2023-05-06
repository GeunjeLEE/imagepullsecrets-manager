from model.credential_model import EcrModel, DockerhubModel
from manager.ecr_manager import EcrManager

import time
import yaml
import base64
import json


class ConfigManager:
    def list_secret_statements(self):
        try:
            with open("./conf/credentials.yaml") as f:
                credentials = yaml.load(f, Loader=yaml.FullLoader)['credentials']

                self._verify_data_struct(credentials)

                for credential in credentials:
                    self._update_current_state(credential)

                return credentials
        except Exception as e:
            raise e

    def list_secret_credentials_by_namespace(self):
        credentials = self.list_secret_statements()

        secret_credential_by_ns = {}
        for credential in credentials:
            secret_credential_by_ns[credential['kubernetes_namespace']] = []

        for credential in credentials:
            secret_credential_by_ns[credential['kubernetes_namespace']].append(credential['name'])

        return secret_credential_by_ns

    def _update_current_state(self, config):
        if config['type'] == 'ECR':
            ecr_authorization_token = self._get_ecr_authorization_token(config['credential'])

            # convert to unix time
            token_expiration_date = time.mktime(ecr_authorization_token['token_expiration_date'].timetuple())
            # server key has token...
            user_name, password = self._data_b64decode(ecr_authorization_token['server']).split(':')
            # token key has repository url...
            url = ecr_authorization_token['token']
            email = 'bot@imagepullsecret.manager'

        elif config['type'] == 'DOCKER':
            token_expiration_date = None
            user_name = config['credential']['docker_user']
            password = config['credential']['docker_password']
            url = config['credential']['docker_registry']
            email = config['credential']['docker_email']

        else:
            raise Exception(f'Unknown type: {config["type"]}')

        data = {
            "auths": {
                url: {
                    "username": user_name,
                    "password": password,
                    "email": email,
                    "auth": self._data_b64encode(f'{user_name}:{password}')
                }
            }
        }

        docker_config_json = base64.b64encode(json.dumps(data).encode()).decode()

        config['token_expiration_date'] = token_expiration_date
        config['dockerconfigjson'] = docker_config_json

    def _get_dockerconfigjson(self, config):
        if config['type'] == 'ECR':
            ecr_authorization_token = self._get_ecr_authorization_token(config['credential'])

            # server key has token...
            user_name, password = self._data_b64decode(ecr_authorization_token['server']).split(':')
            # token key has repository url...
            url = ecr_authorization_token['token']
            email = 'bot@imagepullsecret.manager'

        elif config['type'] == 'DOCKER':
            user_name = config['credential']['docker_user']
            password = config['credential']['docker_password']
            url = config['credential']['docker_registry']
            email = config['credential']['docker_email']

        else:
            raise Exception(f'Unknown type: {config["type"]}')

        data = {
            "auths": {
                url: {
                    "username": user_name,
                    "password": password,
                    "email": email,
                    "auth": self._data_b64encode(f'{user_name}:{password}')
                }
            }
        }

        return base64.b64encode(json.dumps(data).encode()).decode()

    @staticmethod
    def _verify_data_struct(credentials):
        if not credentials:
            return True

        for secret in credentials:
            try:
                if secret['type'] == 'ECR':
                    EcrModel(secret).validate()
                elif secret['type'] == 'DOCKER':
                    DockerhubModel(secret).validate()
            except Exception:
                raise Exception(f'Data invalid format: {secret}')

    @staticmethod
    def _get_ecr_authorization_token(credential):
        ecr_manager = EcrManager(credential)
        token = ecr_manager.get_ecr_token()

        return {
            'server': token['authorizationData'][0]['authorizationToken'],
            'token': token['authorizationData'][0]['proxyEndpoint'],
            'token_expiration_date': token['authorizationData'][0]['expiresAt']
        }

    @staticmethod
    def _data_b64decode(encoded):
        return base64.b64decode(encoded).decode('UTF-8')

    @staticmethod
    def _data_b64encode(input_str):
        input_ascii = input_str.encode("ascii")
        return base64.b64encode(input_ascii).decode("utf-8")
