#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/database/mysql.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 07:14:52 am                                                   #
# Modified   : Thursday July 25th 2024 06:10:53 pm                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""MySQL Database Module"""
from __future__ import annotations

import getpass
import logging
import os
import subprocess
from time import sleep
from typing import Type

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from appstorestream.core.enum import Databases
from appstorestream.infra.config.config import Config
from appstorestream.infra.database.base import DBA, Database

# ------------------------------------------------------------------------------------------------ #
load_dotenv()


# ------------------------------------------------------------------------------------------------ #
#                            MYSQL DATABASE BUILDER                                                #
# ------------------------------------------------------------------------------------------------ #
class MySQLDatabase(Database):
    """MySQL Database Class
    Args:
        dbname (Enum[]): Name of database.
        config_cls (type[Config]): System configuration class.
    """

    def __init__(self, dbname: Databases, config_cls: type[Config] = Config) -> None:
        super().__init__()
        self._config = config_cls()
        self._dbname = f"{self._config.get_environment()}_{dbname.value}"
        self._mysql_credentials = self._config.mysql
        self._connection_string = self._get_connection_string()

    def connect(self, autocommit: bool = False) -> None:
        attempts = 0
        database_started = False
        while attempts < self._config.database.mysql.retries:
            attempts += 1
            try:
                self._engine = sqlalchemy.create_engine(self._connection_string)
                self._connection = self._engine.connect()
                if autocommit is True:
                    self._connection.execution_options(isolation_level="AUTOCOMMIT")
                else:
                    self._connection.execution_options(isolation_level="READ COMMITTED")
                self._is_connected = True
                database_started = True

            except SQLAlchemyError as e:  # pragma: no cover
                self._is_connected = False
                if not database_started:
                    msg = "Database is not started. Starting database..."
                    self._logger.info(msg)
                    self._start_db()
                    database_started = True
                    sleep(3)
                else:
                    msg = f"Database connection failed.\nException type: {type[e]}\n{e}"
                    self._logger.exception(msg)
                    raise
            else:
                return self

    def _get_connection_string(self) -> str:
        """Returns the connection string for the named database."""
        return f"mysql+pymysql://{self._mysql_credentials.username}:{self._mysql_credentials.password}@localhost/{self._dbname}"

    def _start_db(self) -> None:  # pragma: no cover
        subprocess.run([self._config.database.mysql.start], shell=True)


# ------------------------------------------------------------------------------------------------ #
#                          MYSQL DATABASE ADMIN                                                    #
# ------------------------------------------------------------------------------------------------ #


class MySQLDBA(DBA):
    """
    A class to handle various database operations for a MySQL database.

    This class can execute DDL files, check for the existence of databases and tables,
    and manage user passwords using the MySQL command line tool.

    Attributes:
        config_cls (Type[Config]): The configuration class used to get database connection info.
        safe_mode (bool): If True, prevents dropping databases in 'prod' environment.

    Methods:
        create_database(dbname: Databases) -> None: Creates a MySQL database.
        drop_database(dbname: Databases) -> None: Drops a MySQL database with user confirmation, unless in safe mode.
        database_exists(dbname: Databases) -> bool: Checks if the specified database exists.
        table_exists(dbname: Databases, table_name: str) -> bool: Checks if a specific table exists in the specified database.
        create_table(dbname: Databases, ddl_filepath: str) -> None: Creates a table from a DDL file.
        create_tables(dbname: Databases, ddl_directory: str) -> None: Creates tables from all DDL files in a directory.
        _run_bash_script(script_filepath: str) -> None: Runs a bash script with sudo privileges.
    """

    def __init__(self, config_cls: Type[Config] = Config, safe_mode: bool = True) -> None:
        self._config = config_cls()
        self._mysql_credentials = self._config.mysql
        self._env = self._config.get_environment()
        self._safe_mode = safe_mode
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def create_database(self, dbname: Databases) -> None:
        """
        Creates a MySQL database.

        Args:
            dbname (Databases): The name of the database to create.
        """
        dbname = f"{self._env}_{dbname.value}"
        query = f"CREATE DATABASE IF NOT EXISTS `{dbname}`;"
        command = self._build_mysql_command(query)
        self._execute_command(command, f"Creating database {dbname}")

    def drop_database(self, dbname: Databases) -> None:
        """
        Drops a MySQL database with user confirmation, unless in safe mode.

        Args:
            dbname (Databases): The name of the database to drop.
        """
        if self._safe_mode and self._env == 'prod':
            self._logger.error("Dropping databases is not permitted in safe mode in the 'prod' environment.")
            return

        dbname = f"{self._env}_{dbname.value}"
        full_dbname = input(f"Please enter the full name of the database to drop (e.g., '{dbname}'): ").strip()
        if full_dbname == dbname:
            confirm = input(f"Are you sure you want to drop the database '{dbname}'? Type 'YES' to confirm: ").strip().upper()
            if confirm == 'YES':
                query = f"DROP DATABASE IF EXISTS `{dbname}`;"
                command = self._build_mysql_command(query)
                self._execute_command(command, f"Dropping database {dbname}")
            else:
                self._logger.info("Operation cancelled by user.")
        else:
            self._logger.error(f"Database name '{full_dbname}' does not match expected '{dbname}'.")

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

    def create_table(self, dbname: Databases, ddl_filepath: str) -> None:
        """
        Creates a table from a DDL file.

        Args:
            dbname (Databases): The name of the database.
            ddl_filepath (str): The path to the DDL file.
        """
        dbname = f"{self._env}_{dbname.value}"
        self._execute_ddl(dbname, ddl_filepath)

    def create_tables(self, dbname: Databases, ddl_directory: str) -> None:
        """
        Creates tables from all DDL files in a directory.

        Args:
            dbname (Databases): The name of the database.
            ddl_directory (str): The directory containing DDL files.
        """
        try:
            for file_name in sorted(os.listdir(ddl_directory)):
                if file_name.endswith('.sql'):
                    file_path = os.path.join(ddl_directory, file_name)
                    self._logger.info(f"Executing {file_path}...")
                    self.create_table(dbname, file_path)
        except FileNotFoundError as e:
            self._logger.error(f"Directory {ddl_directory} not found.\n{e}")
            raise
        except Exception as e:
            self._logger.error(f"An unknown error occurred.\n{e}")
            raise

    def table_exists(self, dbname: Databases, table_name: str) -> bool:
        """
        Checks if a specific table exists in the specified database.

        Args:
            dbname (Databases): The name of the database to check.
            table_name (str): The name of the table to check for existence.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        dbname = f"{self._env}_{dbname.value}"
        query = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table_name}';"
        command = self._build_mysql_command(query)

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            return table_name in result.stdout
        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Command to check table existence failed with error: {e}")
            return False

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

    def _execute_command(self, command: list[str], action: str) -> None:
        """
        Executes a MySQL command using subprocess.

        Args:
            command (list[str]): The command to execute.
            action (str): The action being performed (for logging).
        """
        try:
            result = subprocess.run(command, text=True, capture_output=True)
            if result.returncode != 0:
                self._logger.error(f"Error {action}: {result.stderr}")
            else:
                self._logger.info(f"Successfully completed {action}")
        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Command {action} failed with error: {e}")

    def _execute_ddl(self, dbname: str, ddl_filepath: str) -> None:
        """
        Executes DDL SQL commands from a file within the specified database.

        Args:
            dbname (str): The name of the database.
            ddl_filepath (str): The path to the DDL file.
        """
        try:
            with open(ddl_filepath, 'r') as ddl_file:
                sql_commands = ddl_file.read()

            use_command = f"USE {dbname};"
            full_query = f"{use_command}\n{sql_commands}"
            command = self._build_mysql_command(full_query)
            result = subprocess.run(command, text=True, capture_output=True)

            if result.returncode != 0:
                self._logger.error(f"Error executing {ddl_filepath}: {result.stderr}")
            else:
                self._logger.info(f"Successfully executed {ddl_filepath}")

        except FileNotFoundError as e:
            self._logger.error(f"SQL file {ddl_filepath} not found.\n{e}")
        except Exception as e:
            self._logger.error(f"An unknown error occurred while executing {ddl_filepath}.\n{e}")

    def _run_bash_script(self, script_filepath: str) -> None:
        """
        Runs a bash script located at the specified path with sudo privileges.

        Args:
            script_filepath (str): The path to the bash script.
        """
        try:
            sudo_password = getpass.getpass(prompt="Enter your sudo password: ")
            command = f"echo {sudo_password} | sudo -S bash {script_filepath}"
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            self._logger.error(f"Script execution failed with error: {e}")
