#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/setup.py                                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 05:31:25 pm                                                 #
# Modified   : Friday July 26th 2024 02:55:46 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Setup Module"""
import logging

from appstorestream.core.enum import DatabaseSet
from appstorestream.infra.config.config import Config
from appstorestream.infra.database.mysql import MySQLDBA

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database(dbname: DatabaseSet, config: Config) -> None:
    """
    Sets up a database by creating it and then creating tables from the provided DDL files.

    Args:
        dbname (DatabaseSet): The enum value representing the database to set up.
        ddl_directory (str): The directory where DDL .sql files are located.

    Raises:
        Exception: If database creation or table setup fails.
    """
    dba = MySQLDBA()
    if dba.database_exists(dbname=dbname):
        # Prompt the user for action
        response = input(f"Database '{dbname.value}' already exists in {config.current_environment}. Do you want to drop and recreate it? Type 'YES' to confirm: ").strip().upper()
        if response == 'YES':
            try:
                dba.drop_database(dbname=dbname)
                dba.create_database(dbname=dbname)
                dba.create_tables(dbname=dbname, ddl_directory=config.setup.database.ddl_directory)
            except Exception as e:
                logger.error(f"Failed to set up database {dbname.value}: {e}")
                raise
        else:
            print(f"Skipping creation of database '{dbname}' in {config.current_environment} environment.")
            return
    else:
        logger.info(f"Setting up database {dbname.value}...")
        dba.create_database(dbname=dbname)
        dba.create_tables(dbname=dbname, ddl_directory=config.setup.database.ddl_directory)
        logger.info(f"Database {dbname.value} in {config.current_environment} environment setup completed successfully.")


def setup_databases(config: Config) -> None:
    """
    Sets up multiple databases by calling setup_database for each database.

    Args:
        ddl_directory (str): The directory where DDL .sql files are located.

    Raises:
        Exception: If setting up any database fails.
    """
    try:
        setup_database(dbname=DatabaseSet.WORKING, config=config)
        setup_database(dbname=DatabaseSet.PERMANENT, config=config)
    except Exception as e:
        logger.error(f"Failed to set up databases: {e}")
        raise

def main() -> None:
    """
    Main function to initialize configuration and set up databases.
    """
    config = Config()
    try:
        setup_databases(config=config)

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
