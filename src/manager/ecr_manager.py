from connector.ecr_connector import EcrConnector


class EcrManager:
    def __init__(self, credential):
        self.ecr_connector = EcrConnector(credential)

    def get_ecr_token(self):
        return self.ecr_connector.get_authorization_token()
