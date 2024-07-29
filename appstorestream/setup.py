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
# Modified   : Monday July 29th 2024 03:46:18 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Setup Module"""
import logging
import os
from datetime import datetime

import click
import numpy as np
import pandas as pd
from dependency_injector.wiring import Provide, inject

from appstorestream.container import AppStoreStreamContainer
from appstorestream.infra.config.config import Config
from appstorestream.infra.database.mysql import MySQLDBA
from appstorestream.infra.repo.project import ProjectRepo


# ------------------------------------------------------------------------------------------------ #
def setup_dependencies():
    container = AppStoreStreamContainer()
    container.init_resources()
    container.wire(
        modules=[
            "appstorestream.application.base.control",
            __name__,
        ]
    )
    # Set up logging explicitly if needed
    logging.getLogger(__name__).info("Logging is set up.")


@inject
def setup_environment(
    env: str,
    config: Config,
    repo: ProjectRepo = Provide[AppStoreStreamContainer.data.project_repo],
) -> None:
    """
    Sets up the environment based on the given environment name.

    Args:
        env (str): The environment name (e.g., 'prod', 'dev', 'test').
        config (Config): A Configuration object.

    Raises:
        ValueError: If the provided environment name is not valid.
    """
    if env not in ["prod", "dev", "test"]:
        raise ValueError(
            f"Invalid environment: {env}. Choose from 'prod', 'dev', 'test'."
        )

    # Change the environment.
    config.change_environment(new_value=env)

    # Setup the database for the environment
    dba = MySQLDBA(config_cls=Config)
    dba.create_database(dbname=config.setup.database.name)
    logging.info("Database created.")

    # Setup Tables
    dba.create_tables(
        dbname=config.setup.database.dbname,
        ddl_directory=config.setup.database.ddl_directory,
    )
    logging.info("Tables created.")
    # Load project table
    dtypes = {
        "project_id": np.int32,
        "dataset": str,
        "category_id": np.int32,
        "category": str,
        "project_priority": np.int32,
        "bookmark": np.int32,
        "n_jobs": np.int32,
        "last_job_id": str,
        "last_job_ended": datetime,
        "last_job_status": str,
        "project_status": str,
    }
    df = pd.read_csv(config.setup.database.project_data_filepath, index_col=None)
    repo.add(projects=df, dtype=dtypes)
    n_projects = len(repo)
    logging.info(f"{n_projects} loaded into the project repository.")


@click.command()
@click.argument("env")
def main(env):
    """
    Setup script for different environments.

    ENV: The environment to set up ('prod', 'dev', 'test').
    """
    config = Config()
    try:
        setup_dependencies()
        setup_environment(env=env, config=config)
        print("Environment setup complete.")
    except ValueError as e:
        print(e)
        click.get_current_context().exit(1)


if __name__ == "__main__":
    main()
