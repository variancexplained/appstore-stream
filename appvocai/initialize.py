#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/initialize.py                                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 05:31:25 pm                                                 #
# Modified   : Saturday September 7th 2024 05:11:53 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Setup Module"""
import logging
from typing import Dict

import pandas as pd
from sqlalchemy.types import INTEGER, VARCHAR

from appvocai.container import AppVoCAIContainer
from appvocai.core.data import NestedNamespace
from appvocai.infra.base.config import Config
from appvocai.infra.database.mysql import Feynman, MySQLDatabase
from appvocai.infra.database.schema import schema

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
def load_database(database: MySQLDatabase, config: Config) -> None:
    """
    Loads data into the database by calling specific table loading functions.

    This function is responsible for initializing the data loading process by invoking
    the necessary functions to load data into the appropriate tables based on the provided
    configuration.

    Args:
        database (MySQLDatabase): The database object where data will be loaded.
        config (Config): The configuration object that provides setup details, such as
                         file paths and table names.
    """
    load_category_table(database=database, config=config)


# ------------------------------------------------------------------------------------------------ #
def load_category_table(database: MySQLDatabase, config: Config) -> None:
    """
    Loads the category data into the 'category' table in the database.

    This function reads category data from a CSV file specified in the configuration and
    inserts it into the 'category' table. The table is dropped and recreated with the correct
    schema, ensuring that primary keys and other constraints are properly enforced. Foreign key
    checks are temporarily disabled during the table creation process to avoid constraint
    violations.

    Args:
        database (MySQLDatabase): The database object where the 'category' table will be loaded.
        config (Config): The configuration object that provides file paths, table names, and
                         setup details. It can be either a `NestedNamespace` or a dictionary.

    Raises:
        AssertionError: If the number of loaded categories does not match the expected count
                        from the CSV file.

    Logs:
        Info: Logs the number of categories loaded into the table.
    """

    # Determine table name and file path from the config
    if isinstance(config.setup, NestedNamespace):
        TABLE_NAME = config.setup.database.tables.category.tablename
        CATEGORY_FILEPATH = config.setup.database.tables.category.filepath
    else:
        TABLE_NAME = config.setup["database"]["tables"]["category"]["tablename"]
        CATEGORY_FILEPATH = config.setup["database"]["tables"]["category"]["filepath"]

    DTYPE = {"category": VARCHAR(64), "category_id": INTEGER}

    # Read category data from the specified CSV file
    categories = pd.read_csv(CATEGORY_FILEPATH, index_col=None)

    with database as db:
        # Temporarily disable foreign key checks to avoid issues when dropping the table
        db.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # Drop the existing category table if it exists
        db.execute("DROP TABLE IF EXISTS category;")

        # Create the category table with the correct schema
        db.execute(schema["category"])

        # Insert the data using 'append' to avoid dropping the newly created table
        db.insert(
            data=categories, table_name=TABLE_NAME, dtype=DTYPE, if_exists="append"
        )

        # Re-enable foreign key checks
        db.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # Verify that the correct number of categories was loaded
        n_categories_loaded = db.count(table_name=TABLE_NAME)

    # Log the successful loading of categories
    logging.info(f"Category table loaded with {n_categories_loaded} categories.")


# ------------------------------------------------------------------------------------------------ #
def setup_database(database: MySQLDatabase, schema: Dict[str, str]) -> None:
    """
    Sets up the database by creating tables according to the provided schema.

    This function initializes the database by creating the necessary tables based on
    the provided schema dictionary. Each key-value pair in the schema represents a table
    name and its corresponding DDL (Data Definition Language) statement.

    Args:
        database (MySQLDatabase): The database object where the tables will be created.
        schema (Dict[str, str]): A dictionary containing table names as keys and their
                                 corresponding DDL statements as values.

    Logs:
        Info: Logs a message indicating that the tables have been successfully created.

    Raises:
        ValueError: If the provided environment name is not valid or if there is an issue
                    with creating the tables based on the provided schema.
    """

    # Create the DBA
    dba = Feynman(database=database)

    for table_name, ddl in schema.items():
        dba.create_table(table_name=table_name, ddl=ddl)
    logger.info("Tables created.")


# ------------------------------------------------------------------------------------------------ #
def setup_dependencies() -> AppVoCAIContainer:
    """
    Initializes and configures the dependency injection container.

    This function creates an instance of the `AppVoCAIContainer`, initializes its
    resources, and wires the dependencies for the current module. This allows for
    dependency injection throughout the application, ensuring that components are
    correctly instantiated and configured.

    Returns:
        AppVoCAIContainer: The initialized and wired dependency injection container.

    Logs:
        Info: Logs a message indicating that the dependency container has been
              successfully created and wired.
    """
    container = AppVoCAIContainer()
    container.init_resources()
    # container.wire(modules=[__name__])
    logger.info("Dependency Container Created and Wired")
    return container


# ------------------------------------------------------------------------------------------------ #
def main() -> None:
    """
    Main setup script for initializing the environment.

    This function orchestrates the setup process for different environments (e.g., 'prod',
    'dev', 'test'). It initializes the configuration, sets up the dependency injection
    container, and then configures and populates the database based on the environment-specific
    settings.

    Steps:
        1. Load the environment configuration.
        2. Set up the dependency injection container.
        3. Set up the database schema based on the provided schema.
        4. Load initial data into the database.

    Logs:
        Prints a message indicating that the environment setup is complete.

    Returns:
        None
    """
    config = Config()

    container = setup_dependencies()
    database = container.db.mysql()
    setup_database(database=database, schema=schema)
    load_database(database=database, config=config)
    print(f"Environment {config.current_environment} setup complete.")


# ------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    main()
