#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/database/base.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday July 24th 2024 11:20:33 pm                                                #
# Modified   : Monday July 29th 2024 03:20:16 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Module provides basic database interface"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import pandas as pd
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError


# ------------------------------------------------------------------------------------------------ #
#                                     DATABASE                                                     #
# ------------------------------------------------------------------------------------------------ #
class Database(ABC):
    """Base class for databases."""

    def __init__(self) -> None:
        self._engine = None
        self._connection = None
        self._transaction = None
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def __enter__(self) -> "Database":
        """Enters a transaction block allowing multiple database operations to be performed as a unit."""
        self.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # pragma: no cover
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
    def connect(self, autocommit: bool = False):
        """Connect to an underlying database.

        Args:
            autocommit (bool): Sets autocommit mode. Default is False.
        """
        pass

    def begin(self):
        """Begins a transaction block."""
        try:
            if self._connection is None:
                self.connect()
            self._transaction = self._connection.begin()
        except AttributeError:
            self.connect()
            self._transaction = self._connection.begin()
        except sqlalchemy.exc.InvalidRequestError:
            self.close()
            self.connect()
            self._transaction = self._connection.begin()

    def commit(self) -> None:
        """Saves pending database operations to the database."""
        try:
            if self._transaction:
                self._transaction.commit()
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during commit.\nException type: {type(e)}\n{e}"
            )
            raise

    def rollback(self) -> None:
        """Restores the database to the state of the last commit."""
        try:
            if self._transaction:
                self._transaction.rollback()
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during rollback.\nException type: {type(e)}\n{e}"
            )
            raise

    def close(self) -> None:
        """Closes the database connection."""
        try:
            if self._connection:
                self._connection.close()
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during connection close.\nException type: {type(e)}\n{e}"
            )
            raise

    def dispose(self) -> None:
        """Disposes the connection and releases resources."""
        try:
            if self._engine:
                self._engine.dispose()
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during engine disposal.\nException type: {type(e)}\n{e}"
            )
            raise

    def insert(
        self,
        data: pd.DataFrame,
        tablename: str,
        dtype: dict = None,
        if_exists: str = "append",
    ) -> int:
        """Inserts data in pandas DataFrame format into the designated table.

        Args:
            data (pd.DataFrame): DataFrame containing the data to add to the designated table.
            tablename (str): The name of the table in the database. If the table does not exist, it will be created.
            dtype (dict): Dictionary of data types for columns.
            if_exists (str): Action to take if table already exists. Valid values are ['append', 'replace', 'fail']. Default = 'append'

        Returns:
            int: Number of rows inserted.
        """
        try:
            return data.to_sql(
                tablename,
                con=self._connection,
                if_exists=if_exists,
                dtype=dtype,
                index=False,
            )
        except SQLAlchemyError as e:
            self._logger.exception(
                f"Exception occurred during insert.\nException type: {type(e)}\n{e}"
            )
            raise

    def query(
        self,
        query: str,
        params: dict = (),
        dtypes: dict = None,
        parse_dates: dict = None,
    ) -> pd.DataFrame:
        """Fetches the results of a query and returns a DataFrame.

        Args:
            query (str): The SQL command
            params (dict): Parameters for the SQL command
            dtypes (dict): Dictionary mapping of column to data types
            parse_dates (dict): Dictionary of columns and keyword arguments for datetime parsing.

        Returns:
            pd.DataFrame: DataFrame containing the query results.
        """
        return pd.read_sql(
            sql=sqlalchemy.text(query),
            con=self._connection,
            params=params,
            dtype=dtypes,
            parse_dates=parse_dates,
        )

    def execute(self, query: str, params: dict = ()) -> sqlalchemy.engine.Result:
        """Execute method reserved primarily for updates, and deletes, as opposed to queries returning data.

        Args:
            query (str): The SQL command
            params (dict): Parameters for the SQL command

        Returns:
            sqlalchemy.engine.Result: Result object containing information about the execution.
        """
        return self._connection.execute(
            statement=sqlalchemy.text(query), parameters=params
        )


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
