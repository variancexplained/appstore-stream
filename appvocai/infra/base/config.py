#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/base/config.py                                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 08:27:38 am                                                   #
# Modified   : Thursday August 29th 2024 09:42:05 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Configuration Classes."""
import logging
import os
from typing import Any, Dict, Union

import yaml
from dotenv import dotenv_values, load_dotenv

from appvocai.core.data import NestedNamespace

# ------------------------------------------------------------------------------------------------ #
load_dotenv()


# ------------------------------------------------------------------------------------------------ #
#                                       CONFIG                                                     #
# ------------------------------------------------------------------------------------------------ #
class Config:
    """
    A class for managing configuration and .env environment variables.

    Attributes:
        _env_file_path (str): Path to the .env file.
        _current_environment (str): Current environment variable value.
        namespace_mode (bool): If True, returneed data can be accessed using dot
            notation.Default = True
    """

    def __init__(self, env_file_path: str = ".env", namespace_mode: bool = True):
        """
        Initialize the Config class with the path to the .env file.

        Args:
            file_path (str): Path to the .env file.
        """
        self._env_file_path = env_file_path
        self._current_environment = self.get_environment()
        self._namespace_mode = namespace_mode
        self._config = self.load_config()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    #  ------------------------------------------------------------------------------------------- #
    @property
    def database(self) -> Union[Dict[str,Any], NestedNamespace]:
        return (
            self.to_namespace(self._config["database"])
            if self._namespace_mode
            else self._config["database"]
        )

    #  ------------------------------------------------------------------------------------------- #
    @property
    def job(self) -> Union[Dict[str,Any], NestedNamespace]:
        return (
            self.to_namespace(self._config["job"])
            if self._namespace_mode
            else self._config["job"]
        )

    #  ------------------------------------------------------------------------------------------- #
    @property
    def mysql(self) -> Union[Dict[str,Any], NestedNamespace]:
        """
        Returns MySQL database name, backup location, and related parameters.
        """
        config = {}
        # Get config from .env file.
        config["username"] = os.getenv("MYSQL_USERNAME")
        config["password"] = os.getenv("MYSQL_PWD")
        config["port"] = os.getenv("MYSQL_PORT")
        config["host"] = os.getenv("MYSQL_HOST")
        config["startup"] = os.getenv("MYSQL_STARTUP")
        return self.to_namespace(config) if self._namespace_mode else config

    #  ------------------------------------------------------------------------------------------- #
    @property
    def proxy(self) -> str:
        """
        Returns proxy server configuration.
        """
        # Get config from .env file.
        dns = os.getenv("WEBSHARE_DNS")
        username = os.getenv("WEBSHARE_USER")
        pwd = os.getenv("WEBSHARE_PWD")
        port = os.getenv("WEBSHARE_PORT")
        return f"http://{username}:{pwd}@{dns}:{port}"

    #  ------------------------------------------------------------------------------------------- #
    @property
    def current_environment(self) -> str:
        return self._current_environment

    #  ------------------------------------------------------------------------------------------- #
    @property
    def filepath(self) -> str:
        """Returns the configuration filepath for the current environment."""
        env = self.get_environment().lower()

        return os.path.join(os.getenv("CONFIG_FOLDER", "config"), f"{env}.yaml")

    #  ------------------------------------------------------------------------------------------- #
    def change_environment(self, new_value: str) -> None:
        """
        Changes the environment variable and updates it in the current process.

        Args:
            new_value (str): The new value to set for the key.
        """
        key = "ENV"
        # Load existing values
        env_values = dotenv_values(self._env_file_path)
        # Add/update the key-value pair
        env_values[key] = new_value
        # Write all values back to the file
        with open(self._env_file_path, "w") as file:
            for k, v in env_values.items():
                file.write(f"{k}={v}\n")
        # Update the environment variable in the current process
        os.environ[key] = new_value
        print(
            f"Updated {key} to {new_value} in {self._env_file_path} and current process"
        )

    #  ------------------------------------------------------------------------------------------- #
    def get_environment(self) -> str:
        """
        Gets the environment variable

        Returns:
            str: The value of the environment variable.
        """
        return os.getenv("ENV", "dev")

    #  ------------------------------------------------------------------------------------------- #
    def load_environment(self) -> None:
        """
        Load environment variables from the .env file.
        """
        load_dotenv(self._env_file_path, override=True)

    #  ------------------------------------------------------------------------------------------- #
    def load_config(self) -> Dict[str,Any]:
        """
        Loads the base configuration as well as environment specific config.

        """

        config_filepath_env = self.filepath

        if config_filepath_env is not None:
            # Load env config
            with open(config_filepath_env, "r") as env_config_file:
                env_config = yaml.safe_load(env_config_file)

            config = {**env_config}

            return config
        else:
            msg = f"Base config filepath not found in .env file. Unable to load config."
            self._logger.exception(msg)
            raise RuntimeError(msg)

    #  ------------------------------------------------------------------------------------------- #
    def to_namespace(self, config: Dict[str,Any]) -> NestedNamespace:
        return NestedNamespace(config)
