#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/utils.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 08:20:44 am                                                   #
# Modified   : Monday July 29th 2024 03:38:34 am                                                   #
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
