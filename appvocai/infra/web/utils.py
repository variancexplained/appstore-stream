#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/web/utils.py                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 08:20:44 am                                                   #
# Modified   : Tuesday August 27th 2024 06:26:13 pm                                                #
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
