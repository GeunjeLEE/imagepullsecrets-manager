from manager.secret_manager import SecretManager
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
    secret_manager = SecretManager()
    config = _get_config()

    for secret_config in config:
        secret_manager.set_config(secret_config)
        secret_manager.run()

    secret_manager.clean_up(config)

if __name__ == '__main__':
    main()

