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
# Modified   : Monday July 29th 2024 03:52:52 am                                                   #
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

from appstorestream.infra.config.config import Config
from appstorestream.infra.database.mysql import MySQLDBA


# ------------------------------------------------------------------------------------------------ #
def setup_environment(
    env: str,
    config: Config,
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
    dba.create_database(dbname=config.config.setup.database.dbname)
    logging.info("Database created.")

    # Setup Tables
    dba.create_tables(
        dbname=config.config.setup.database.dbname,
        ddl_directory=config.config.setup.database.ddl_directory,
    )
    logging.info("Tables created.")


@click.command()
@click.argument("env")
def main(env):
    """
    Setup script for different environments.

    ENV: The environment to set up ('prod', 'dev', 'test').
    """
    config = Config()
    try:
        setup_environment(env=env, config=config)
        print("Environment setup complete.")
    except ValueError as e:
        print(e)
        click.get_current_context().exit(1)


if __name__ == "__main__":
    main()
