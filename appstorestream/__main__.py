#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/__main__.py                                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 10:59:26 am                                                   #
# Modified   : Thursday July 25th 2024 04:34:22 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from appstorestream.infra.config import Config
from appstorestream.container import AppStoreStreamContainer
# ------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    container = AppStoreStreamContainer()
    container.config.from_dict(Config().load_config())
    container.init_resources()
