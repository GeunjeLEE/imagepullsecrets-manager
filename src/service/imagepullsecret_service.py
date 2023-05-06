from manager.kubernetes_manager import KubernetesManager
from manager.config_manager import ConfigManager


class ImagepullsecretService:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.kubernetes_manager = KubernetesManager()

    def scan(self):
        secret_statements = self.config_manager.list_secret_statements()
        for secret_statement in secret_statements:
            self.kubernetes_manager.scan_secret(secret_statement)

    def clean_up(self):
        secret_credentials_by_ns = self.config_manager.list_secret_credentials_by_namespace()
        self.kubernetes_manager.cleanup_secret(secret_credentials_by_ns)
