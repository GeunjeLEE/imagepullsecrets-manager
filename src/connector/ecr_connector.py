import logging
import boto3

logging.basicConfig(level=logging.INFO)


class EcrConnector:
    def __init__(self, credential):
        self.client = self._login(credential)

    def get_authorization_token(self):
        try:
            return self.client.get_authorization_token()
        except Exception as e:
            raise e

    @staticmethod
    def _login(credential):
        aws_access_key_id = credential['aws_access_key_id']
        aws_secret_access_key = credential['aws_secret_access_key']
        aws_ecr_repository_region = credential['aws_ecr_repository_region']

        try:
            sess = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            return sess.client('ecr', region_name=aws_ecr_repository_region)
        except Exception as e:
            raise e
