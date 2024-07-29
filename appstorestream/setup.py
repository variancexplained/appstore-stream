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
# Modified   : Monday July 29th 2024 02:46:27 pm                                                   #
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

from appstorestream.container import AppStoreStreamContainer
from appstorestream.infra.base.config import Config
from appstorestream.infra.database.mysql import MySQLDBA
from appstorestream.infra.repo.project import ProjectRepo


# ------------------------------------------------------------------------------------------------ #
@inject
def setup_database(
    env: str,
    config: Config,
    repo: ProjectRepo = Provide[AppStoreStreamContainer.data.project_repo],
) -> None:
    """
    Sets up the database based on the given environment name.

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
    dba.create_database(dbname=config.database.dbname)
    print("Database created.")

    # Setup Tables
    dba.create_tables(
        dbname=config.database.dbname,
        ddl_directory=config.database.ddl_directory,
    )
    print("Tables created.")

    # Load project table
    dtypes = {
        "project_id": INTEGER,
        "dataset": VARCHAR,
        "category_id": INTEGER,
        "category": VARCHAR,
        "project_priority": INTEGER,
        "bookmark": INTEGER,
        "n_jobs": INTEGER,
        "last_job_id": VARCHAR,
        "last_job_ended": DATETIME,
        "last_job_status": VARCHAR,
        "project_status": VARCHAR,
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


def setup_dependencies():
    container = AppStoreStreamContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    print("Dependency Container Created and Wired")


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
        setup_database(env=env, config=config)
        print("Environment setup complete.")
    except ValueError as e:
        print(e)
        click.get_current_context().exit(1)


if __name__ == "__main__":
    main()
