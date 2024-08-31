#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/setup.py                                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 05:31:25 pm                                                 #
# Modified   : Saturday August 31st 2024 02:02:08 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Setup Module"""
import logging
from datetime import datetime

import click
import pandas as pd
from dependency_injector.wiring import Provide, inject
from sqlalchemy.types import DATETIME, INTEGER, VARCHAR

from appvocai.container import AppVoCAIContainer
from appvocai.core.data import NestedNamespace
from appvocai.infra.base.config import Config
from appvocai.infra.database.base import Database
from appvocai.infra.database.schema import schema

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
@inject
def setup_database(
    database: Database
) -> None:
    """
    Sets up the database based on the current environment name.

    Args:
        database (Database): A Database object.

    Raises:
        ValueError: If the provided environment name is not valid.
    """

    # Setup Tables
    dba.create_tables(
        dbname=dbname,
        ddl_directory=ddl_directory,
    )
    logger.info("Tables created.")

    # Load project table
    dtypes = {
        "category_id": INTEGER,
        "category": VARCHAR,
    }
    try:
        df = pd.read_csv(config.database.project_data_filepath, index_col=None)
        repo.add(projects=df, dtype=dtypes)
        n_projects = len(repo)
        print(f"{n_projects} loaded into the project repository.")
    except ValueError:
        print(f"Project table already exists.")
    except Exception:
        print(f"Project table already exists.")


def setup_dependencies() -> AppVoCAIContainer:
    container = AppVoCAIContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    logger.info("Dependency Container Created and Wired")
    return container


@click.command()
@click.argument("env")
def main(env):
    """
    Setup script for different environments.

    ENV: The environment to set up ('prod', 'dev', 'test').
    """

    config = Config()
    try:
        container = setup_dependencies()
        database = container.db.mysql
        setup_database(config=config, database=database)
        print("Environment setup complete.")
    except ValueError as e:
        print(e)
        click.get_current_context().exit(1)


if __name__ == "__main__":
    main()
