#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/database/base.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday July 24th 2024 11:20:33 pm                                                #
# Modified   : Thursday August 29th 2024 07:35:48 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Module provides basic database interface"""
from __future__ import annotations

import logging
import traceback
from abc import ABC, abstractmethod
from typing import Any, Dict, Literal, Optional

import pandas as pd
import sqlalchemy
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import Connection, RootTransaction
from sqlalchemy.exc import SQLAlchemyError

# ------------------------------------------------------------------------------------------------ #
#                                     DATABASE                                                     #
# ------------------------------------------------------------------------------------------------ #

class Database(ABC):
    """Base class for databases with connection pooling, transaction management, and DataFrame handling."""

    def __init__(self, connection_string: str) -> None:
        """Initialize the Database class with a connection string.

        Args:
            connection_string (str): Database connection string.
        """
        self._engine: Optional[Engine] = create_engine(connection_string, pool_size=5, max_overflow=10)  # Connection pooling
        self._connection: Optional[Connection] = None
        self._transaction: Optional[RootTransaction] = None
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def __enter__(self) -> Database:
        """Enter a transaction block, allowing multiple database operations to be performed as a unit."""
        self.begin()
        return self



    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: Optional[traceback.TracebackType]) -> None:
        """Special method takes care of properly releasing the object's resources to the operating system."""
        if exc_type is not None:
            try:
                self.rollback()
            except SQLAlchemyError as e:
                self._logger.exception(
                    f"Exception occurred during rollback.\nException type: {type(e)}\n{e}"
                )
                raise
            self._logger.exception(
                f"Exception occurred.\nException type: {exc_type}\n{exc_value}\n{traceback}"
            )
            raise
        else:
            self.commit()
        self.close()


    @abstractmethod
    def connect(self, autocommit: bool = False) -> Database:
        """Connect to an underlying database.

        Args:
            autocommit (bool): Sets autocommit mode. Default is False.
        """
        pass

    def begin(self) -> None:
        """Begin a transaction block."""
        try:
            if self._connection is None:
                self.connect()
            if self._connection is not None:
                self._transaction = self._connection.begin()
        except AttributeError:
            self.connect()
            if self._connection is not None:
                self._transaction = self._connection.begin()
        except sqlalchemy.exc.InvalidRequestError:
            self.close()
            self.connect()
            if self._connection is not None:
                self._transaction = self._connection.begin()

    def commit(self) -> None:
        """Save pending database operations to the database."""
        try:
            if self._transaction:
                self._transaction.commit()
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during commit.\nException type: {type(e)}\n{e}"
            )
            raise

    def rollback(self) -> None:
        """Restore the database to the state of the last commit."""
        try:
            if self._transaction:
                self._transaction.rollback()
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during rollback.\nException type: {type(e)}\n{e}"
            )
            raise

    def close(self) -> None:
        """Close the database connection."""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None  # Set to None after closing
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during connection close.\nException type: {type(e)}\n{e}"
            )
            raise

    def dispose(self) -> None:
        """Dispose the engine and release resources."""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None  # Set to None after disposing
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during engine disposal.\nException type: {type(e)}\n{e}"
            )
            raise

    def insert(
        self,
        data: pd.DataFrame,
        tablename: str,
        dtype: Optional[Dict[str,Any]] = None,
        if_exists: Literal['fail', 'replace', 'append'] = "append",
    ) -> int:
        """Insert data in pandas DataFrame format into the designated table.

        Args:
            data (pd.DataFrame): DataFrame containing the data to add to the designated table.
            tablename (str): The name of the table in the database. If the table does not exist, it will be created.
            dtype (dict): Dictionary of data types for columns.
            if_exists (str): Action to take if table already exists. Valid values are ['append', 'replace', 'fail']. Default = 'append'

        Returns:
            int: Number of rows inserted. Returns 0 if the DataFrame is empty.
        """

        if self._connection is None:
            raise ValueError("Database connection is not established.")

        if data.empty:
            self._logger.warning("No data to insert. DataFrame is empty.")
            return 0

        try:
            inserted_rows = data.to_sql(
                tablename,
                con=self._connection,
                if_exists=if_exists,
                dtype=dtype,
                index=False,
            )
            self._logger.info(f"Inserted {inserted_rows} rows into {tablename}.")
            if inserted_rows is not None:
                return inserted_rows
            else:
                return 0
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during insert into {tablename}.\nException type: {type(e)}\n{e}"
            )
            raise

    def query(
        self,
        query: str,
        params: Optional[Dict[str,Any]] = None,
        dtypes: Optional[Dict[str,Any]] = None,
        parse_dates: Optional[Dict[str,Any]] = None,
    ) -> pd.DataFrame:
        """Fetch the results of a query and return a DataFrame.

        Args:
            query (str): The SQL command.
            params (dict): Parameters for the SQL command. Should match placeholders in the query.
            dtypes (dict): Dictionary mapping of column names to data types.
            parse_dates (dict): Dictionary of columns and keyword arguments for datetime parsing.

        Returns:
            pd.DataFrame: DataFrame containing the query results.
        """

        if self._connection is None:
            raise ValueError("Database connection is not established.")

        self._logger.info(f"Executing query: {query} with params: {params}")
        return pd.read_sql(
            sql=text(query),
            con=self._connection,
            params=params,
            dtype=dtypes,
            parse_dates=parse_dates,
        )

    def execute(self, query: str, params: Optional[Dict[str,Any]] = None) -> sqlalchemy.engine.Result:
        """Execute a SQL command reserved primarily for updates and deletes.

        Args:
            query (str): The SQL command.
            params (dict): Parameters for the SQL command. Should match placeholders in the query.

        Returns:
            sqlalchemy.engine.Result: Result object containing information about the execution.

        Raises:
            ValueError: If parameters are required but not provided.
        """

        if self._connection is None:
            raise ValueError("Database connection is not established.")

        if not params and self._requires_parameters(query):
            raise ValueError("Parameters are required for this query.")

        self._logger.info(f"Executing command: {query} with params: {params}")
        return self._connection.execute(
            statement=text(query), parameters=params
        )

    def _requires_parameters(self, query: str) -> bool:
        """Check if the query requires parameters.

        Args:
            query (str): The SQL command.

        Returns:
            bool: True if parameters are required, False otherwise.
        """
        return ":" in query or "?" in query  # Adjust based on your parameter style

# ------------------------------------------------------------------------------------------------ #
#                                DATABASE ADMIN                                                    #
# ------------------------------------------------------------------------------------------------ #
class DBA(ABC):
    """ "Abstract base class for building databases from DDL"""

    @abstractmethod
    def create_database(self, dbname: str) -> None:
        """
        Creates a MySQL database.

        Args:
            dbname (str): The name of the database to create.
        """

    @abstractmethod
    def drop_database(self, dbname: str) -> None:
        """
        Drops a MySQL database with user confirmation, unless in safe mode.

        Args:
            dbname (str): The name of the database to drop.
        """

    @abstractmethod
    def database_exists(self, dbname: str) -> bool:
        """
        Checks if the specified database exists.

        Args:
            dbname (str): The database name to check for existence.

        Returns:
            bool: True if the database exists, False otherwise.
        """

    @abstractmethod
    def create_table(self, dbname: str, ddl_filepath: str) -> None:
        """
        Creates a table from a DDL file.

        Args:
            dbname (str): The name of the database.
            ddl_filepath (str): The path to the DDL file.
        """

    @abstractmethod
    def create_tables(self, dbname: str, ddl_directory: str) -> None:
        """
        Creates tables from all DDL files in a directory.

        Args:
            dbname (str): The name of the database.
            ddl_directory (str): The directory containing DDL files.
        """

    @abstractmethod
    def table_exists(self, dbname: str, table_name: str) -> bool:
        """
        Checks if a specific table exists in the specified database.

        Args:
            dbname (str): The name of the database to check.
            table_name (str): The name of the table to check for existence.

        Returns:
            bool: True if the table exists, False otherwise.
        """
