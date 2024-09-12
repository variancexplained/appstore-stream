#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /acquire/infra/database/mysql.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 07:14:52 am                                                   #
# Modified   : Monday September 9th 2024 04:57:55 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""MySQL Database Module"""
from __future__ import annotations

import getpass
import logging
import os
import re
import subprocess
from time import sleep
from typing import Dict, List, Type

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.exc import (
    IntegrityError,
    ProgrammingError,
    SQLAlchemyError,
    StagealError,
)

from acquire.core.data import NestedNamespace
from acquire.infra.base.config import Config
from acquire.infra.database.base import DBA, Database

# ------------------------------------------------------------------------------------------------ #
load_dotenv()


# ------------------------------------------------------------------------------------------------ #
#                            MYSQL DATABASE BUILDER                                                #
# ------------------------------------------------------------------------------------------------ #
class MySQLDatabase(Database):
    """
    MySQL Database Class for managing connections and interactions with a MySQL database.

    This class extends the `Database` class and provides
    functionalities specific to MySQL databases, including
    connection management and configuration handling.

    Args:
        config_cls (Type[Config], optional): The system configuration
                                              class that provides
                                              MySQL connection settings.
                                              Defaults to `Config`.

    Attributes:
        _dbname (str): The name of the database, appended with the
                       current environment.
        _mysql_credentials: MySQL credentials obtained from the
                            configuration class.
        _connection_string (str): The connection string used to
                                  connect to the MySQL database.
        _engine: The SQLAlchemy engine for managing connections.
        _connection: The current database connection object.

    Methods:
        __init__(config_cls: Type[Config]) -> None:
            Initializes the MySQLDatabase instance, sets up the
            connection string, and prepares the database for
            interactions.

    Example:
        db = MySQLDatabase()
    """

    __dbname = "appvocai"

    def __init__(self, config_cls: Type[Config] = Config) -> None:
        self._config = config_cls()

        self._dbname = f"{self.__dbname}_{self._config.get_environment()}"
        self._mysql_credentials = self._config.mysql
        self._connection_string = self._get_connection_string()
        self._engine = None
        self._connection = None
        super().__init__(connection_string=self._connection_string)

    @property
    def name(self) -> str:
        return self._dbname

    def begin(self) -> None:
        """Begin a new MySQL database transaction."""
        # MySQL-specific transaction management could go here
        super().begin()  # Call the base method if needed

    def connect(self, autocommit: bool = False) -> MySQLDatabase:
        """
        Establish a connection to the MySQL database.

        This method attempts to create a connection to the database using the
        configured connection string. It supports retries if the connection
        fails. The isolation level of the connection can be set to either
        "AUTOCOMMIT" or "READ COMMITTED" based on the `autocommit` parameter.

        Args:
            autocommit (bool, optional): A flag indicating whether the
                                        connection should be in autocommit
                                        mode. Defaults to False.

        Returns:
            MySQLDatabase: The current instance of the MySQLDatabase class.

        Raises:
            SQLAlchemyError: If the connection to the database fails after
                            the specified number of retries.

        Example:
            db = MySQLDatabase()
            db.connect(autocommit=True)

        Notes:
            - The method will attempt to connect to the database multiple times
            if initial connection attempts fail.
            - The connection engine is created only once, and subsequent calls
            to connect will reuse the existing engine.
            - The method will log attempts to connect and any errors encountered.
        """
        attempts = 0
        retries = (
            self._config.database.retries
            if isinstance(self._config.database, NestedNamespace)
            else self._config.database["retries"]
        )

        while attempts < retries:
            attempts += 1
            try:
                if self._engine is None:
                    self._logger.debug(
                        f"Creating engine for connection string: {self._connection_string}"
                    )
                    self._engine = sqlalchemy.create_engine(self._connection_string)
                if self._connection is None:
                    self._logger.debug("Attempting to connect to the database.")
                    self._connection = self._engine.connect()

                if autocommit:
                    self._connection.execution_options(isolation_level="AUTOCOMMIT")
                else:
                    self._connection.execution_options(isolation_level="READ COMMITTED")

                self._logger.info("Database connection established successfully.")
                return self

            except SQLAlchemyError as e:
                self._logger.warning(
                    f"Attempt {attempts} to connect to the database failed."
                )
                if attempts < retries:
                    self._logger.info(
                        "Attempting to start database and retry connection."
                    )
                    self._start_db()
                    sleep(3)
                else:
                    msg = f"Database connection failed after {attempts} attempts. Exception type: {type(e)}\n{e}"
                    self._logger.exception(msg)
                    raise
        msg = f"Database connection failed after multiple attempts."
        self._logger.exception(msg)
        raise

    def _get_connection_string(self) -> str:
        """
        Construct and return the connection string for the MySQL database.

        This method retrieves the username and password from the MySQL
        credentials and constructs a connection string in the format required
        for connecting to a MySQL database using the PyMySQL driver.

        Returns:
            str: The connection string formatted as
                "mysql+pymysql://username:password@localhost/dbname".

        Raises:
            KeyError: If the username or password is not found in the
                    MySQL credentials.

        Notes:
            - The connection string is used to establish a connection to the
            MySQL database.
            - The database is assumed to be hosted locally (localhost).
        """
        username = (
            self._mysql_credentials.username
            if isinstance(self._mysql_credentials, NestedNamespace)
            else self._mysql_credentials["username"]
        )
        password = (
            self._mysql_credentials.password
            if isinstance(self._mysql_credentials, NestedNamespace)
            else self._mysql_credentials["password"]
        )
        return f"mysql+pymysql://{username}:{password}@localhost/{self._dbname}"

    def _start_db(self) -> None:
        """
        Start the MySQL database.

        This method initiates the MySQL database as per the configuration
        settings. The specific starting command or procedure can be
        defined within this method, depending on the requirements.

        Raises:
            Exception: If the database fails to start. The specific
                    exception type will depend on the implementation
                    details of the database startup process.

        Notes:
            - Ensure that the database service is configured properly
            before calling this method.
            - The method relies on the `start` attribute from the
            database configuration to determine how to start the
            database.
        """
        start = (
            self._config.database.start
            if isinstance(self._config.database, NestedNamespace)
            else self._config.database["start"]
        )

        subprocess.run([start], shell=True)

    def close(self) -> None:
        """
        Close the database connection.

        This method closes the active database connection and disposes
        of the database engine. It ensures that resources are released
        and that the connection is properly terminated.

        Notes:
            - If a connection is active, it will be closed and the
            connection reference will be set to None.
            - If the database engine exists, it will be disposed of to
            free up resources, and the engine reference will also
            be set to None.
            - Calling this method multiple times has no effect after
            the connection has been closed and resources have been
            disposed.

        Example:
            db = MySQLDatabase()
            db.connect()
            # Perform database stages
            db.close()
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None


# ------------------------------------------------------------------------------------------------ #
#                         MYSQL DATABASE ADMIN - FEYNMAN                                           #
# ------------------------------------------------------------------------------------------------ #
FOREIGN_KEY_CHECKS_OFF = "FOREIGN_KEY_CHECKS = 0"
FOREIGN_KEY_CHECKS_ON = "FOREIGN_KEY_CHECKS = 1"


class Feynman(DBA):
    """ "Abstract base class for building databases from DDL"""

    def __init__(self, database: MySQLDatabase) -> None:
        self._database = database
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def create_table(self, table_name: str, ddl: str, force: bool = False) -> None:
        """
        Creates a table from a DDL file.

        Args:
            table_name (str): The name of the table.
            ddl (str): The data definition language.
        """
        # If the table exists and force is True, drop the table
        if self.table_exists(table_name=table_name):
            # If force is True, drop and recreate the table
            if force:
                self._drop_table(table_name=table_name)
                self._create_table(table_name=table_name, ddl=ddl)
            # If force is False, get use approval
            else:
                message = f"The {table_name} table already exists."
                if self._user_approves(table_name=table_name, message=message):
                    self._drop_table(table_name=table_name)
                    self._create_table(table_name=table_name, ddl=ddl)
                else:
                    self._logger.info(
                        f"Table {table_name} was not created. It already exists."
                    )
        else:
            self._create_table(table_name=table_name, ddl=ddl)

    def create_tables(self, schema: Dict[str, str], force: bool = False) -> None:
        """
        Creates tables from all DDL files in a directory.

        Args:
            schema (Dict[str,str]): Dictionary with keys indicating the
                table name and ddl as values.
            force (bool): If True, existing tables will be overwritten
                by new tables. If False, the other user will be prompted
                to keep or overwrite the table.
        """

        for table_name, ddl in schema.items():
            self.create_table(table_name=table_name, ddl=ddl, force=force)

    def table_exists(self, table_name: str) -> bool:
        """
        Checks if a specific table exists in the specified database.

        Args:
            dbname (str): The name of the database to check.
            table_name (str): The name of the table to check for existence.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        dbname = self._database.name
        query = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table_name}';"
        with self._database as db:
            result = db.query(query=query)
            return len(result) > 0

    def drop_table(self, table_name: str) -> None:
        """Drops the designated table from the current databases.

        Args:
            table_name (str): Name of the table to drop.

        """
        if self._data_exists(table_name=table_name):
            message = f"Table {table_name} is not empty."
            if self._user_approves(table_name=table_name, message=message):
                self._drop_table(table_name=table_name)
            else:
                self._logger.info(
                    f"Table {table_name} was not dropped from the {self._database.name} database."
                )
        else:
            self._drop_table(table_name=table_name)
            self._logger.info(
                f"Table {table_name} was dropped from the {self._database.name} database."
            )

    def _user_approves(self, table_name: str, message: str) -> bool:
        message = message + " To continue enter the table name."
        response = input(message)
        return response == table_name

    def _drop_table(self, table_name: str) -> None:
        try:
            query = f"DROP TABLE IF EXISTS {table_name};"
            with self._database as db:
                db.execute(FOREIGN_KEY_CHECKS_OFF)
                db.execute(query=query)
                db.execute(FOREIGN_KEY_CHECKS_ON)
            self._logger.info(
                f"Table {table_name} was dropped from the {self._database.name} database."
            )
        except StagealError as e:
            self._logger.exception(e)
        except IntegrityError as e:
            self._logger.exception(e)
        except SQLAlchemyError as e:
            self._logger.exception(e)
        except ProgrammingError as e:
            self._logger.exception(e)

    def _data_exists(self, table_name: str) -> bool:
        with self._database as db:
            count = db.count(table_name=table_name)
        if isinstance(count, int):
            return count > 0
        else:
            return False

    def _create_table(self, table_name: str, ddl: str) -> None:
        try:
            with self._database as db:
                db.execute(query=ddl)
                self._logger.info(
                    f"Created table {table_name} in {self._database.name} database."
                )
        except StagealError as e:
            self._logger.exception(e)
        except IntegrityError as e:
            self._logger.exception(e)
        except SQLAlchemyError as e:
            self._logger.exception(e)
        except ProgrammingError as e:
            self._logger.exception(e)

    def create_database(self, dbname: str) -> None:
        """
        Creates a MySQL database.

        Args:
            dbname (str): The name of the database to create.
        """
        pass

    def drop_database(self, dbname: str) -> None:
        """
        Drops a MySQL database with user confirmation, unless in safe mode.

        Args:
            dbname (str): The name of the database to drop.
        """
        pass

    def database_exists(self, dbname: str) -> bool:
        """
        Checks if the specified database exists.

        Args:
            dbname (str): The database name to check for existence.

        Returns:
            bool: True if the database exists, False otherwise.
        """
        raise NotImplementedError


# ------------------------------------------------------------------------------------------------ #
class Shannon(DBA):
    """
    A class to handle various database stages for a MySQL database.

    This class can execute DDL files, check for the existence of databases and tables,
    and manage user passwords using the MySQL command line tool.

    Attributes:
        config_cls (Type[Config]): The configuration class used to get database connection info.
        safe_mode (bool): If True, prevents dropping databases in 'prod' environment.

    Methods:
        create_database(dbname: str) -> None: Creates a MySQL database.
        drop_database(dbname: str) -> None: Drops a MySQL database with user confirmation, unless in safe mode.
        database_exists(dbname: str) -> bool: Checks if the specified database exists.
        table_exists(dbname: str, table_name: str) -> bool: Checks if a specific table exists in the specified database.
        create_table(dbname: str, ddl_filepath: str) -> None: Creates a table from a DDL file.
        create_tables(dbname: str, ddl_directory: str) -> None: Creates tables from all DDL files in a directory.
        _run_bash_script(script_filepath: str) -> None: Runs a bash script with sudo privileges.
    """

    def __init__(
        self, config_cls: Type[Config] = Config, safe_mode: bool = True
    ) -> None:
        self._config = config_cls()
        self._mysql_credentials = self._config.mysql
        self._env = self._config.get_environment()
        self._safe_mode = safe_mode
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def create_database(self, dbname: str) -> None:
        """
        Creates a MySQL database.

        Args:
            dbname (str): The name of the database to create.
        """
        dbname = self._format_dbname(dbname)
        query = f"CREATE DATABASE IF NOT EXISTS `{dbname}`;"
        command = self._build_mysql_command(query)
        self._execute_command(command, f"Creating database {dbname}")
        msg = f"Database: {dbname} created."
        self._logger.info(msg)

    def drop_database(self, dbname: str) -> None:
        """
        Drops a MySQL database with user confirmation, unless in safe mode.

        Args:
            dbname (str): The name of the database to drop.
        """
        if self._safe_mode and self._env == "prod":
            self._logger.info(
                "Dropping databases is not permitted in safe mode in the 'prod' environment."
            )
            return

        dbname = self._format_dbname(dbname)
        full_dbname = input(
            f"Please enter the full name of the database to drop (e.g., '{dbname}'): "
        ).strip()
        if full_dbname == dbname:
            confirm = (
                input(
                    f"Are you sure you want to drop the database '{dbname}'? Type 'YES' to confirm: "
                )
                .strip()
                .upper()
            )
            if confirm.lower() == "yes":
                query = f"DROP DATABASE IF EXISTS `{dbname}`;"
                command = self._build_mysql_command(query)
                self._execute_command(command, f"Dropping database {dbname}")
                self._logger.info(f"Dropped database: {dbname}.")
            else:
                print("Stage cancelled by user.")
        else:
            print(f"Database name '{full_dbname}' does not match expected '{dbname}'.")

    def database_exists(self, dbname: str) -> bool:
        """
        Checks if the specified database exists.

        Args:
            dbname (str): The database name to check for existence.

        Returns:
            bool: True if the database exists, False otherwise.
        """
        dbname = self._format_dbname(dbname)
        query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{dbname}';"
        command = self._build_mysql_command(query)

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            return dbname in result.stdout
        except subprocess.CalledProcessError as e:
            self._logger.exception(
                f"Command to check database existence failed with error: {e}"
            )
            return False

    def create_table(self, dbname: str, ddl_filepath: str) -> None:
        """
        Creates a table from a DDL file.

        Args:
            dbname (str): The name of the database.
            ddl_filepath (str): The path to the DDL file.
        """
        dbname = self._format_dbname(dbname)
        self._execute_ddl(dbname, ddl_filepath)

    def create_tables(self, dbname: str, ddl_directory: str) -> None:
        """
        Creates tables from all DDL files in a directory.

        Args:
            dbname (str): The name of the database.
        """

        try:
            for file_name in sorted(os.listdir(ddl_directory)):
                if file_name.endswith(".sql"):
                    file_path = os.path.join(ddl_directory, file_name)
                    self._logger.info(f"Executing ddl in {file_path}..")
                    self.create_table(dbname, file_path)
        except FileNotFoundError as e:
            self._logger.exception(f"Directory {ddl_directory} not found.\n{e}")
            raise
        except Exception as e:
            self._logger.exception(f"An unknown error occurred.\n{e}")
            raise

    def table_exists(self, table_name: str, dbname: str) -> bool:
        """
        Checks if a specific table exists in the specified database.

        Args:
            dbname (str): The name of the database to check.
            table_name (str): The name of the table to check for existence.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        dbname = self._format_dbname(dbname)
        query = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table_name}';"
        command = self._build_mysql_command(query)

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            return table_name in result.stdout
        except subprocess.CalledProcessError as e:
            self._logger.exception(
                f"Command to check table existence failed with error: {e}"
            )
            return False

    def _build_mysql_command(self, query: str) -> list[str]:
        """
        Builds the MySQL command with optional password.

        Args:
            query (str): The SQL query to execute.

        Returns:
            list[str]: The command and arguments to execute.
        """
        host = (
            self._mysql_credentials.host
            if isinstance(self._mysql_credentials, NestedNamespace)
            else self._mysql_credentials["host"]
        )
        username = (
            self._mysql_credentials.username
            if isinstance(self._mysql_credentials, NestedNamespace)
            else self._mysql_credentials["username"]
        )
        command = [
            "mysql",
            "-h",
            host,
            "-u",
            username,
            "-e",
            query,
        ]
        password = (
            self._mysql_credentials.password
            if isinstance(self._mysql_credentials, NestedNamespace)
            else self._mysql_credentials["password"]
        )
        command.insert(3, f"-p{password}")

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
                self._logger.exception(f"Error {action}: {result.stderr}")
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
            with open(ddl_filepath, "r") as ddl_file:
                sql_commands = ddl_file.read()

            use_command = f"USE {dbname};"
            full_query = f"{use_command}\n{sql_commands}"
            command = self._build_mysql_command(full_query)
            result = subprocess.run(command, text=True, capture_output=True)

            if result.returncode != 0:
                self._logger.exception(
                    f"Error executing {ddl_filepath}: {result.stderr}"
                )
            else:
                self._logger.info(f"Successfully executed {ddl_filepath}")

        except FileNotFoundError as e:
            self._logger.exception(f"SQL file {ddl_filepath} not found.\n{e}")
        except Exception as e:
            self._logger.exception(
                f"An unknown error occurred while executing {ddl_filepath}.\n{e}"
            )

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
            self._logger.info(f"Successfully executed {script_filepath}")
        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Script execution failed with error: {e}")

    def _format_dbname(self, dbname: str) -> str:
        return f"{dbname}_{self._env}"

    def _parse_table_name(self, filepath: str) -> List[str]:
        table_name_pattern = re.compile(r"CREATE TABLE\s+(\w+)", re.IGNORECASE)

        with open(filepath, "r") as file:
            sql_content = file.read()

        matches = table_name_pattern.findall(sql_content)

        if matches:
            return matches
        return []
