#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/core/enum.py                                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 02:31:31 pm                                              #
# Modified   : Thursday August 29th 2024 05:05:09 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from enum import Enum


# ------------------------------------------------------------------------------------------------ #
class Category(Enum):
    BUSINESS = 6000
    WEATHER = 6001
    UTILITIES = 6002
    TRAVEL = 6003
    SPORTS = 6004
    SOCIAL_NETWORKING = 6005
    REFERENCE = 6006
    PRODUCTIVITY = 6007
    PHOTO_VIDEO = 6008
    NEWS = 6009
    NAVIGATION = 6010
    MUSIC = 6011
    LIFESTYLE = 6012
    HEALTH_FITNESS = 6013
    GAMES = 6014
    FINANCE = 6015
    ENTERTAINMENT = 6016
    EDUCATION = 6017
    BOOKS = 6018
    MEDICAL = 6020
    NEWSSTAND = 6021
    CATALOGS = 6022
    FOOD_DRINK = 6023
    SHOPPING = 6024
    DEVELOPER_TOOLS = 6026
    GRAPHICS_DESIGN = 6027

# ------------------------------------------------------------------------------------------------ #
class ContentType(Enum):
    APPDATA = "AppData"
    APPREVIEW = "AppReview"

# ------------------------------------------------------------------------------------------------ #
class ProjectStatus(Enum):
    ACTIVE = "Active"
    IDLE = "Idle"

# ------------------------------------------------------------------------------------------------ #
class JobStatus(Enum):
    CREATED = "Created"
    SCHEDULED = "Scheduled"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELED = "Canceled"

# ------------------------------------------------------------------------------------------------ #
class ProjectFrequency(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

# ------------------------------------------------------------------------------------------------ #
class AppDataURLType(Enum):
    SCREENSHOT = "screenshot"
    IPAD = "ipad"
