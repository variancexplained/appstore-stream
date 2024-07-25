#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/core/enum.py                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 22nd 2024 10:19:32 pm                                                   #
# Modified   : Thursday July 25th 2024 02:06:14 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from enum import Enum


# ------------------------------------------------------------------------------------------------ #
class JobStatus(Enum):
    CREATED = "created"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    CREATED = "created"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"

class Databases(Enum):
    WORKING = "appstore_stream_working_db"
    PERMANENT = "appstore_stream_db"