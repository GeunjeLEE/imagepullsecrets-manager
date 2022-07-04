import logging
import boto3
logging.basicConfig(level=logging.INFO)


class EcrConnector():
    def __init__(self, aws_credentials):
        self.aws_access_key_id = aws_credentials['aws_access_key_id']
        self.aws_secret_access_key = aws_credentials['aws_secret_access_key']
        self.aws_ecr_repository_region = aws_credentials['aws_ecr_repository_region']
        self.login()

    def login(self):
        try:
            sess = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        except Exception as e:
            raise e

        self.client = sess.client('ecr', region_name=self.aws_ecr_repository_region)

    def get_authorization_token(self):
        try:
            return self.client.get_authorization_token()
        except Exception as e:
            raise e
