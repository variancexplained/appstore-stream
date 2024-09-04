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
# Modified   : Wednesday September 4th 2024 04:51:58 am                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Configuration Classes."""
import logging
import os
from typing import Any, Dict, Union, cast

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
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._env_file_path = env_file_path
        self._current_environment = self.get_environment()
        self._namespace_mode = namespace_mode
        self._config = self.load_config()

    #  ------------------------------------------------------------------------------------------- #
    @property
    def database(self) -> Union[Dict[str, Any], NestedNamespace]:
        return (
            self.to_namespace(self._config["database"])
            if self._namespace_mode
            else self._config["database"]
        )

    #  ------------------------------------------------------------------------------------------- #
    @property
    def job(self) -> Union[Dict[str, Any], NestedNamespace]:
        return (
            self.to_namespace(self._config["job"])
            if self._namespace_mode
            else self._config["job"]
        )

    #  ------------------------------------------------------------------------------------------- #
    @property
    def mysql(self) -> Union[Dict[str, Any], NestedNamespace]:
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
    def extractor(self) -> NestedNamespace:
        config = self.load_config()
        return self.to_namespace(config["extractor"])

    #  ------------------------------------------------------------------------------------------- #
    @property
    def filepath(self) -> str:
        """Returns the configuration filepath for the current environment."""
        env = self.get_environment().lower()

        return os.path.join(os.getenv("CONFIG_FOLDER", "config"), f"{env}.yaml")

    #  ------------------------------------------------------------------------------------------- #
    @property
    def setup(self) -> Union[Dict[str, Any], NestedNamespace]:
        return (
            self.to_namespace(self._config["setup"])
            if self._namespace_mode
            else self._config["setup"]
        )

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
        # Load the current environment
        self.load_environment()
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
    def load_config(self) -> Dict[str, Any]:
        """
        Loads the base configuration as well as the environment-specific configuration.

        This method merges the base configuration with environment-specific settings
        by loading them separately and then combining them into a single dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing the combined configuration, with
                            environment-specific settings overriding the base settings.
        """
        base_config = self._load_base_config()
        env_config = self._load_env_config()
        return {**base_config, **env_config}

    #  ------------------------------------------------------------------------------------------- #
    def _load_base_config(self) -> Dict[str, Any]:
        """
        Loads the base configuration from a YAML file.

        The file path is determined by the `CONFIG_BASE_FILEPATH` environment variable,
        or it defaults to `config/base.yaml`. This method reads the YAML file and returns
        its contents as a dictionary.

        Returns:
            Dict[str, Any]: The base configuration as a dictionary.

        Raises:
            FileNotFoundError: If the base configuration file is not found.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        base_config = {}

        filepath = os.getenv("CONFIG_BASE_FILEPATH", "config/base.yaml")
        content = "base configuration"
        base_config = self.read_yaml(filepath=filepath, content=content)
        return base_config

    #  ------------------------------------------------------------------------------------------- #
    def _load_env_config(self) -> Dict[str, Any]:
        """
        Loads the environment-specific configuration from a YAML file.

        The file path is determined by the `filepath` attribute of the class. If the
        `filepath` is not set, a `RuntimeError` is raised. This method reads the YAML
        file and returns its contents as a dictionary.

        Returns:
            Dict[str, Any]: The environment-specific configuration as a dictionary.

        Raises:
            RuntimeError: If the environment-specific configuration file path is not set.
            FileNotFoundError: If the environment-specific configuration file is not found.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        env_config = {}
        filepath = self.filepath
        if not filepath:
            msg = "Unable to determine the environment filepath."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        content = "environment configuration"
        env_config = self.read_yaml(filepath=filepath, content=content)
        return env_config

    #  ------------------------------------------------------------------------------------------- #
    def read_yaml(self, filepath: str, content: str) -> Dict[str, Any]:
        """
        Reads a YAML file and returns its contents as a dictionary.

        This method attempts to load a YAML file from the specified `filepath`. If the
        file is found and successfully parsed, its contents are returned as a dictionary.
        If the file is not found or there is an error parsing the YAML content, an exception
        is logged and re-raised.

        Args:
            filepath (str): The path to the YAML file to be read.
            content (str): A description of the content being read, used for logging purposes.

        Returns:
            Dict[str, Any]: The contents of the YAML file as a dictionary.

        Raises:
            FileNotFoundError: If the specified file is not found at the given `filepath`.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        try:
            with open(filepath, "r") as file:
                data = yaml.safe_load(file)
                return cast(Dict[str, Any], data)
        except FileNotFoundError:
            self._logger.exception(
                f"Unable to read {content}. File not found at {filepath}."
            )
            raise
        except yaml.YAMLError as e:
            self._logger.exception(
                f"Exception while reading {content} from {filepath}\n{e}"
            )
            raise

    #  ------------------------------------------------------------------------------------------- #
    def to_namespace(self, config: Dict[str, Any]) -> NestedNamespace:
        """
        Converts a configuration dictionary to a NestedNamespace object.

        This method transforms a flat or nested dictionary of configuration settings
        into a `NestedNamespace` object, which allows for attribute-style access to
        the configuration values.

        Args:
            config (Dict[str, Any]): The configuration dictionary to be converted.

        Returns:
            NestedNamespace: The configuration wrapped in a `NestedNamespace` object.
        """
        return NestedNamespace(config)
