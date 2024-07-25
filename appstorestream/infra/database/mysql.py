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
# Modified   : Thursday July 25th 2024 02:14:56 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""MySQL Database Module"""
from __future__ import annotations
import logging
import os
import subprocess
from datetime import datetime
from time import sleep
from typing import Optional

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from appstorestream.core.enum import Databases
from appstorestream.infra.config import Config
from appstorestream.infra.database.base import Database

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
