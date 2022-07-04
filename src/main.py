from service.secret_service import SecretService
import yaml
import logging
import sys


def _get_config():
    try:
        with open("./conf/secret.yaml") as f:
            return yaml.load(f, Loader=yaml.FullLoader)['secrets']
    except FileNotFoundError as e:
        logging.error(f"config file not found: {e}")
        sys.exit(1)


def main():
    secret_service = SecretService()
    config = _get_config()

    for secret_config in config:
        secret_service.set_config(secret_config)
        secret_service.run()

    secret_service.clean_up(config)


if __name__ == '__main__':
    main()
