from model.credential_model import EcrModel, DockerhubModel
from service.secret_service import SecretService
import yaml
import logging
import sys


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
            raise Exception(f'Data invalid : {secret}')


def _get_config():
    try:
        with open("./conf/credentials.yaml") as f:
            credentials = yaml.load(f, Loader=yaml.FullLoader)['credentials']

            _verify_data_struct(credentials)

            return credentials
    except Exception as e:
        raise e


def main():
    credentials = _get_config()
    secret_service = SecretService(credentials)

    secret_service.run()
    secret_service.clean_up()


if __name__ == '__main__':
    main()
