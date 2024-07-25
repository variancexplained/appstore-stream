#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/config/chgenv.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday July 23rd 2024 12:08:29 am                                                  #
# Modified   : Thursday July 25th 2024 02:48:49 pm                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #

import click

from appstorestream.infra.config.config import Config


@click.command()
@click.argument("env", type=str)
def chgenv(env):
    """
    Change the environment setting.

    ENV is the environment to set (e.g., 'dev' or 'prod').
    """
    if env not in ["dev", "test", "prod"]:
        click.echo("Invalid environment. Choose 'dev' or 'prod'.")
        return

    cm = Config()
    cm.change_environment(new_value=env)
    click.echo(f"Environment set to {env}")


if __name__ == "__main__":
    chgenv()
