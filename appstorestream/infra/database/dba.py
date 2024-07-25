#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/database/dba.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday July 24th 2024 11:37:44 pm                                                #
# Modified   : Thursday July 25th 2024 04:58:32 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""MySQL Database Administration Module"""
import os
import logging
import subprocess
from typing import Type

from appstorestream.core.enum import Databases
from appstorestream.infra.database.base import DBA
from appstorestream.infra.config import Config
# ------------------------------------------------------------------------------------------------ #
#                          MYSQL DATABASE ADMIN                                                    #
# ------------------------------------------------------------------------------------------------ #

class MySQLDBA(DBA):
    """
    A class to handle various database operations for a MySQL database.

    This class can execute DDL files, check for the existence of databases and tables,
    and manage user passwords using the MySQL command line tool.

    Attributes:
        dbname (Optional[Databases]): The name of the database. Optional.
        ddl_directory (Optional[str]): The directory where the DDL .sql files are stored. Optional.
        config_cls (Type[Config]): The configuration class used to get database connection info.

    Methods:
        execute_ddl(ddl_filepath: str) -> None: Executes a single DDL SQL file.
        execute_all_ddl(ddl_directory: str) -> None: Executes all DDL .sql files in the specified directory.
        database_exists(dbname: Databases) -> bool: Checks if the specified database exists.
        table_exists(dbname: str, table_name: str) -> bool: Checks if a specific table exists in the specified database.
        update_user_password(username: str, new_password: str) -> None: Updates the password for a MySQL user.
    """

    def __init__(self, dbname: Databases, config_cls: Type[Config] = Config) -> None:
        self._config = config_cls()
        self._dbname = f"{self._config.get_environment()}_{dbname.value}"
        self._mysql_credentials = self._config.mysql
        self._env = self._config.get_environment()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def execute_ddl(self, ddl_filepath: str) -> None:
        """
        Executes a single DDL SQL file using the MySQL command line tool.

        Args:
            ddl_filepath (str): The path to the .sql file to be executed.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """
        try:
            # Read the SQL commands from the file
            with open(ddl_filepath, 'r') as ddl_file:
                sql_commands = ddl_file.read()

            # Construct the USE command and concatenate with the SQL commands
            use_command = f"USE {self._dbname};"
            full_query = f"{use_command}\n{sql_commands}"

            # Construct the command for executing the SQL
            command = self._build_mysql_command(full_query)
            result = subprocess.run(command, text=True, capture_output=True)


            if result.returncode != 0:
                self._logger.error(f"Error executing {ddl_filepath}: {result.stderr}")
            else:
                self._logger.info(f"Successfully executed {ddl_filepath}")

        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Command in {ddl_filepath} failed with error: {e}")

    def execute_all_ddl(self, ddl_directory: str) -> None:
        """
        Executes all DDL .sql files in the specified directory.

        Args:
            ddl_directory (str): Directory containing SQL files.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
            Exception: For any other errors that occur during execution.
        """
        try:
            for file_name in os.listdir(ddl_directory):
                if file_name.endswith('.sql'):
                    file_path = os.path.join(ddl_directory, file_name)
                    self._logger.info(f"Executing {file_path}...")
                    self.execute_ddl(file_path)
        except FileNotFoundError as e:
            self._logger.error(f"Directory {ddl_directory} not found.\n{e}")
            raise
        except Exception as e:
            self._logger.error(f"An unknown error occurred.\n{e}")
            raise

    def database_exists(self, dbname: Databases) -> bool:
        """
        Checks if the specified database exists.

        Args:
            dbname (Databases): The database name to check for existence.

        Returns:
            bool: True if the database exists, False otherwise.
        """
        dbname = f"{self._env}_{dbname.value}"
        query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{dbname}';"
        command = self._build_mysql_command(query)

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            return dbname in result.stdout
        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Command to check database existence failed with error: {e}")
            return False

    def table_exists(self, dbname: Databases, table_name: str) -> bool:
        """
        Checks if a specific table exists in the specified database.

        Args:
            dbname (str): The name of the database to check.
            table_name (str): The name of the table to check for existence.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        dbname = f"{self._env}_{dbname.value}"
        query = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table_name}';"
        command = self._build_mysql_command(query=query)

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            return table_name in result.stdout
        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Command to check table existence failed with error: {e}")
            return False

    def update_user_password(self, username: str, new_password: str) -> None:
        """
        Updates the password for a MySQL user.

        Args:
            username (str): The MySQL username whose password is to be updated.
            new_password (str): The new password for the MySQL user.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """
        query = f"ALTER USER '{username}'@'localhost' IDENTIFIED WITH mysql_native_password BY '{new_password}';"
        command = self._build_mysql_command(query)

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            if result.returncode != 0:
                self._logger.error(f"Error updating password for user {username}: {result.stderr}")
            else:
                self._logger.info(f"Successfully updated password for user {username}")

        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Command to update password for user {username} failed with error: {e}")

    def _build_mysql_command(self, query: str) -> list[str]:
        """
        Builds the MySQL command with optional password.

        Args:
            query (str): The SQL query to execute.

        Returns:
            list[str]: The command and arguments to execute.
        """
        command = [
            'mysql',
            '-h', self._mysql_credentials.host,
            '-u', self._mysql_credentials.username,
            '-e', query
        ]
        if self._mysql_credentials.password:
            command.insert(3, f"-p{self._mysql_credentials.password}")

        return command
