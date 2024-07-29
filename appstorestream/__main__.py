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
# Modified   : Monday July 29th 2024 04:40:33 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from appstorestream.container import AppStoreStreamContainer
from appstorestream.infra.config.config import Config

# ------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    container = AppStoreStreamContainer()
    container.init_resources()
    container.wire(modules=[__name__])
