#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoC: AppStore Voice of the Customer                                              #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvoc/infrastructure/web/utils.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvoc                                          #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:45:44 am                                                   #
# Modified   : Friday July 19th 2024 04:45:56 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Web Utils"""
import sys

import requests


# ------------------------------------------------------------------------------------------------ #
def getsize(response: requests.Response) -> int:
    """Returns the size of an HTTP response object.

    Args:
        response (requests.Response): An HTTP Response object.

    """
    try:
        size = int(response.headers["content-length"])
    except KeyError:
        size = sys.getsizeof(response.json())
    except Exception:
        size = sys.getsizeof(response)
    return size
