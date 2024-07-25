#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/config/config.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 08:27:38 am                                                   #
# Modified   : Thursday July 25th 2024 03:03:47 pm                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Configuration Classes."""
import os
from typing import Union

import pandas as pd
import yaml
from dotenv import dotenv_values, load_dotenv

from appstorestream.core.data import NestedNamespace

# ------------------------------------------------------------------------------------------------ #
load_dotenv()


# ------------------------------------------------------------------------------------------------ #
#                                       CONFIG                                                     #
# ------------------------------------------------------------------------------------------------ #
class Config:
    """
    A class for managing configuration and .env environment variables.

    Attributes:
        _file_path (str): Path to the .env file.
        _current_environment (str): Current environment variable value.
        namespace_mode (bool): If True, returneed data can be accessed using dot
            notation.Default = True
    """

    def __init__(self, file_path: str = ".env", namespace_mode: bool = True):
        """
        Initialize the Config class with the path to the .env file.

        Args:
            file_path (str): Path to the .env file.
        """
        self._file_path = file_path
        self._current_environment = self.get_environment()
        self._namespace_mode = namespace_mode
        self._config = self.load_config()

    #  ------------------------------------------------------------------------------------------- #
    @property
    def setup(self) -> Union[dict, NestedNamespace]:
        """
        Returns parameters for app setup
        """
        config = self._config["setup"]
        return self.to_namespace(config) if self._namespace_mode else config
    #  ------------------------------------------------------------------------------------------- #
    @property
    def appdata(self) -> Union[dict, NestedNamespace]:
        """
        Returns parameters for the app data request
        """
        config = self._config["appdata"]
        return self.to_namespace(config) if self._namespace_mode else config

    #  ------------------------------------------------------------------------------------------- #
    @property
    def review(self) -> Union[dict, NestedNamespace]:
        """
        Returns parameters for the review request
        """
        config = self._config["review"]
        return self.to_namespace(config) if self._namespace_mode else config

    #  ------------------------------------------------------------------------------------------- #
    @property
    def get_categories(self) -> pd.DataFrame:
        """
        Returns category data as a dataframe.
        """
        config = self.read_config()
        return pd.DataFrame(config["category"]).T

    #  ------------------------------------------------------------------------------------------- #
    def get_category(self, category_id: str) -> Union[dict, NestedNamespace]:
        """
        Returns category data given a category id.
        """

        try:
            category = self._config["category"][category_id]
            return self.to_namespace(category) if self._namespace_mode else category
        except KeyError:
            print(f"Category id {category_id} was not found.")

    #  ------------------------------------------------------------------------------------------- #
    @property
    def logging(self) -> Union[dict, NestedNamespace]:
        """
        Logging configuration
        """
        config = self._config["logging"]
        return self.to_namespace(config) if self._namespace_mode else config

    #  ------------------------------------------------------------------------------------------- #
    @property
    def cloud(self) -> Union[dict, NestedNamespace]:
        """
        Returns parameters for the app data request
        """
        config = self._config["cloud"]
        return self.to_namespace(config) if self._namespace_mode else config

    #  ------------------------------------------------------------------------------------------- #
    @property
    def monitor(self) -> Union[dict, NestedNamespace]:
        """
        Returns parameters for the app data request
        """
        config = self._config["monitor"]
        return self.to_namespace(config) if self._namespace_mode else config

    #  ------------------------------------------------------------------------------------------- #
    @property
    def current_environment(self) -> str:
        return self._current_environment

    #  ------------------------------------------------------------------------------------------- #
    def change_environment(self, new_value: str) -> None:
        """
        Changes the environment variable and updates it in the current process.

        Args:
            new_value (str): The new value to set for the key.
        """
        key = "ENV"
        # Load existing values
        env_values = dotenv_values(self._file_path)
        # Add/update the key-value pair
        env_values[key] = new_value
        # Write all values back to the file
        with open(self._file_path, "w") as file:
            for k, v in env_values.items():
                file.write(f"{k}={v}\n")
        # Update the environment variable in the current process
        os.environ[key] = new_value
        print(f"Updated {key} to {new_value} in {self._file_path} and current process")

    #  ------------------------------------------------------------------------------------------- #
    def get_environment(self):
        """
        Gets the environment variable

        Returns:
            str: The value of the environment variable.
        """
        return os.getenv("ENV")

    #  ------------------------------------------------------------------------------------------- #
    def load_environment(self):
        """
        Load environment variables from the .env file.
        """
        load_dotenv(self._env_file, override=True)

    #  ------------------------------------------------------------------------------------------- #
    @property
    def mysql(self) -> Union[dict, NestedNamespace]:
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
    def redis(self) -> Union[dict, NestedNamespace]:
        """
        Returns Redis in-memory database config.
        """
        config = self._config["database"]["redis"]
        return self.to_namespace(config) if self._namespace_mode else config

    #  ------------------------------------------------------------------------------------------- #
    def load_config(self) -> dict:
        """
        Loads the base configuration as well as environment specific config.

        """
        env = os.getenv("ENV", "dev")
        # Get the base config filename
        base_config_filepath = os.path.join(
            os.getenv("CONFIG_FOLDER", "config"), "base.yaml"
        )
        env_config_filepath = os.path.join(os.getenv("CONFIG_FOLDER", "config"), f"{env}.yaml")
        # Open config files.
        with open(base_config_filepath, "r") as base_file:
            base_config = yaml.safe_load(base_file)

        with open(env_config_filepath, "r") as env_file:
            env_config = yaml.safe_load(env_file)

        # Merge configurations, with environment-specific settings overriding base settings
        config = {**base_config, **env_config}

        return config

    #  ------------------------------------------------------------------------------------------- #
    def to_namespace(self, config: dict) -> NestedNamespace:
        return NestedNamespace(config)
