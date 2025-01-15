from os import getenv
from typing import Dict, List
from dotenv import load_dotenv
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)

class ConfigSQLServer:
    """
    Classe para configuração de conexão com SQL Server.
    """
    REQUIRED_ENV_VARS = ["DB_USERNAME", "DB_PASSWORD", "DB_HOST", "DB_NAME", "DB_DRIVER"]

    def __init__(self):
        """Inicializa a configuração e valida as variáveis de ambiente."""
        load_dotenv()
        logger.info("Carregando variáveis de ambiente do arquivo .env.")
        self._load_config()
        self._validate_config()

    def _load_config(self) -> None:
        """Carrega variáveis de ambiente."""
        self.DB_USERNAME = getenv("DB_USERNAME")
        self.DB_PASSWORD = getenv("DB_PASSWORD")
        self.DB_HOST = getenv("DB_HOST")
        self.DB_NAME = getenv("DB_NAME")
        self.DB_DRIVER = getenv("DB_DRIVER")
        logger.info("Variáveis de ambiente carregadas com sucesso.")

    def _validate_config(self) -> None:
        """Valida se todas as variáveis obrigatórias estão presentes."""
        missing_vars = self._get_missing_vars()
        if missing_vars:
            logger.error(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
            raise EnvironmentError(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")

    def _get_missing_vars(self) -> List[str]:
        """Retorna as variáveis obrigatórias ausentes."""
        return [var for var in self.REQUIRED_ENV_VARS if not getattr(self, var, None)]

    def test_connection(self) -> None:
        """Testa a conectividade com o banco de dados."""
        logger.info(f"Testando conexão com o banco de dados em {self.DB_HOST}...")
        # Aqui você pode implementar um teste real, como uma conexão simples.

    def get_config_dict(self) -> Dict[str, str]:
        """Retorna as configurações como dicionário."""
        return {var: getattr(self, var) for var in self.REQUIRED_ENV_VARS}

    @property
    def DATABASE_URL(self) -> str:
        """Constrói a URL de conexão com o banco de dados."""
        return (
            f"mssql+aioodbc://"
            f"{quote_plus(self.DB_USERNAME)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}/{self.DB_NAME}?"
            f"driver={quote_plus(self.DB_DRIVER)}"
        )
