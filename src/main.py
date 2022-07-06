from service.secret_service import SecretService
import yaml
import logging
import sys


def _verify_credential(secrets):
    expected_credential_keys = {
        'ECR': ["aws_access_key_id", "aws_secret_access_key", "aws_ecr_repository_region"],
        'DOCKER': ["docker_registry", "docker_user", "docker_password", "docker_email"]
    }

    # need schematics or something?
    for secret in secrets:
        actual_keys = secret['credential'].keys()
        expected_keys = expected_credential_keys[secret['type']]

        for expected_key in expected_keys:
            if expected_key not in actual_keys:
                raise Exception(f'incorrect credential!, [{expected_key}] not found')


def _get_config():
    try:
        with open("./conf/secret.yaml") as f:
            secrets = yaml.load(f, Loader=yaml.FullLoader)['secrets']

            if secrets:
                _verify_credential(secrets)

            return secrets
    except FileNotFoundError as e:
        logging.error(f"config file not found: {e}")
        sys.exit(1)


def main():
    secrets = _get_config()
    secret_service = SecretService(secrets)

    secret_service.run()
    secret_service.clean_up()


if __name__ == '__main__':
    main()
