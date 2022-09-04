"""Handles load/save of the configuration to JSON file."""
import json
import logging
import os
from netorg_core import ports

class NetorgConfigurationAdapter(ports.NetorgConfigurationPort):
    """Configuration file adapter where the config file is JSON in the home directory."""
    # pylint: disable=line-too-long

    def __init__(self) -> None:
        self.__logger = logging.getLogger("netorg")

    # overriding abstract method
    def load(self) -> dict:
        """Load configuration from a JSON file in the home directory."""
        config_filename = self.__get_config_filename()
        self.__logger.debug(f"NetorgConfigurationAdapter.load() loading {config_filename}")
        with open(config_filename, encoding='utf8') as json_file:
            return json.load(json_file)

    # overriding abstract method
    def save(self,config: dict):
        """Save configuration."""
        if config:
            config_filename = self.__get_config_filename()
            self.__logger.debug(f"NetorgConfigurationAdapter.save() saving config to {config_filename}")
            with open(config_filename, 'w', encoding='utf8') as netorg_config_file:
                netorg_config_file.write(json.dumps(config, indent=2))

    def __get_config_filename(self) -> str:
        """Return the fully qualified config filename e.g. /a/b/.netorg.cfg"""
        directory = os.path.expanduser('~')
        filename = '.netorg.cfg'
        return os.path.join(directory,filename)
