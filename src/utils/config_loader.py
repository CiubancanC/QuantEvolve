"""
Configuration loader for QuantEvolve
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager for QuantEvolve"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Load configuration from YAML file and environment variables

        Args:
            config_path: Path to config YAML file (default: config/default_config.yaml)
        """
        # Load environment variables
        load_dotenv()

        # Default config path
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"

        # Load YAML config
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)

        # Override with environment variables where applicable
        self._apply_env_overrides()

    def _apply_env_overrides(self):
        """Apply environment variable overrides to config"""
        # API key
        if os.getenv("OPENROUTER_API_KEY"):
            if "llm" not in self._config:
                self._config["llm"] = {}
            self._config["llm"]["api_key"] = os.getenv("OPENROUTER_API_KEY")

        # Model selection
        if os.getenv("SMALL_MODEL"):
            self._config["llm"]["small_model"] = os.getenv("SMALL_MODEL")
        if os.getenv("LARGE_MODEL"):
            self._config["llm"]["large_model"] = os.getenv("LARGE_MODEL")

        # Paths
        if os.getenv("DATA_PATH"):
            self._config["data_path"] = os.getenv("DATA_PATH")
        if os.getenv("RESULTS_PATH"):
            self._config["results_path"] = os.getenv("RESULTS_PATH")
        if os.getenv("LOGS_PATH"):
            self._config["logs_path"] = os.getenv("LOGS_PATH")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key

        Args:
            key: Configuration key (e.g., 'evolution.num_islands')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value by dot-separated key

        Args:
            key: Configuration key
            value: Value to set
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    @property
    def raw(self) -> Dict[str, Any]:
        """Get raw configuration dictionary"""
        return self._config

    def save(self, path: str):
        """
        Save configuration to YAML file

        Args:
            path: Output file path
        """
        with open(path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration

    Args:
        config_path: Path to config file

    Returns:
        Config instance
    """
    return Config(config_path)
