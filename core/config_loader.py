import yaml
import configparser
from typing import List, Dict
from pydantic import BaseModel
from collections import defaultdict
from sentry_sdk import capture_exception


class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        try:
            config_dict = self.yaml_to_dict(self.config_path)
            return AppConfig(**config_dict)
        except Exception as error:
            capture_exception(error)

    @staticmethod
    def yaml_to_dict(file_path):
        """Load the YAML configuration file."""
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return config_dict

    @staticmethod
    def ini_to_dict(file_path):
        """Load the INI/TOML configuration file."""
        config = configparser.ConfigParser()
        config.read(file_path)

        config_dict = defaultdict(dict)

        for section in config.sections():
            section_parts = section.split('.')
            if len(section_parts) == 1:
                config_dict[section] = dict(config.items(section))
            else:
                sub_dict = config_dict[section_parts[0]]
                for part in section_parts[1:]:
                    sub_dict = sub_dict.setdefault(part, {})
                sub_dict.update(config.items(section))

        return dict(config_dict)

    @property
    def server(self):
        """Retrieve the server config."""
        return self.config.server

    @property
    def rds(self):
        """Retrieve the RDS Config."""
        return self.config.rds

    @property
    def error(self):
        """Returns the Config for Error Tracking."""
        return self.config.error


class ServerConfig(BaseModel):
    debug: bool = False
    env: str = 'development'
    is_using_windows: bool = False
    secret_key: str = ''
    gdal_libaray_path: str = ''
    geos_libaray_path: str = ''


class DBConfig(BaseModel):
    db_name: str = ''
    db_user: str = ''
    db_password: str = ''
    db_host: str = ''
    db_port: str = '5432'
    db_replica_host: str = ''


class ErrorConfig(BaseModel):
    teams_webhook: str = ''
    sentry_dsn: str = ''


class AppConfig(BaseModel):
    server: ServerConfig = ServerConfig()
    rds: DBConfig = DBConfig()
    error: ErrorConfig = ErrorConfig()


class DotDict(dict):
    """Dictionary with dot notation access to nested keys."""

    def __getattr__(self, item):
        try:
            value = self[item]
            if isinstance(value, dict):
                return DotDict(value)
            return value
        except KeyError:
            raise AttributeError(f"Attribute {item} not found")

    def __setattr__(self, key, value):
        self[key] = value
