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
# Modified   : Sunday September 8th 2024 07:00:57 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from enum import Enum
from typing import Optional


# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
class Category(Enum):
    """Enumeration of application categories with associated Apple category codes.

    Each category is represented by a unique code and a display name. This enum
    provides a mapping between the category codes used in the application and their
    human-readable names as recognized by Apple.

    Attributes:
        BOOKS (tuple): Category for Books with code 6018.
        BUSINESS (tuple): Category for Business with code 6000.
        CATALOGS (tuple): Category for Catalogs with code 6022.
        DEVELOPER_TOOLS (tuple): Category for Developer Tools with code 6026.
        EDUCATION (tuple): Category for Education with code 6017.
        ENTERTAINMENT (tuple): Category for Entertainment with code 6016.
        FINANCE (tuple): Category for Finance with code 6015.
        FOOD_DRINK (tuple): Category for Food & Drink with code 6023.
        GAMES (tuple): Category for Games with code 6014.
        GRAPHICS_DESIGN (tuple): Category for Graphics & Design with code 6027.
        HEALTH_FITNESS (tuple): Category for Health & Fitness with code 6013.
        LIFESTYLE (tuple): Category for Lifestyle with code 6012.
        MEDICAL (tuple): Category for Medical with code 6020.
        MUSIC (tuple): Category for Music with code 6011.
        NAVIGATION (tuple): Category for Navigation with code 6010.
        NEWS (tuple): Category for News with code 6009.
        NEWSSTAND (tuple): Category for Newsstand with code 6021.
        PHOTO_VIDEO (tuple): Category for Photo & Video with code 6008.
        PRODUCTIVITY (tuple): Category for Productivity with code 6007.
        REFERENCE (tuple): Category for Reference with code 6006.
        SOCIAL_NETWORKING (tuple): Category for Social Networking with code 6005.
        SHOPPING (tuple): Category for Shopping with code 6024.
        SPORTS (tuple): Category for Sports with code 6004.
        TRAVEL (tuple): Category for Travel with code 6003.
        UTILITIES (tuple): Category for Utilities with code 6002.
        WEATHER (tuple): Category for Weather with code 6001.

    Methods:
        __new__(cls, code: int, name: str) -> Category:
            Create a new instance of the Category enum, setting the value and description.

    Example Usage:
        To access the category's description and value:

        >>> category = Category.BOOKS
        >>> print(category.name)         # Output: 'BOOKS'
        >>> print(category.value)        # Output: 6018
        >>> print(category.description) # Output: 'Books'
    """

    BOOKS = (6018, "Books")
    BUSINESS = (6000, "Business")
    CATALOGS = (6022, "Catalogs")
    DEVELOPER_TOOLS = (6026, "Developer Tools")
    EDUCATION = (6017, "Education")
    ENTERTAINMENT = (6016, "Entertainment")
    FINANCE = (6015, "Finance")
    FOOD_DRINK = (6023, "Food & Drink")
    GAMES = (6014, "Games")
    GRAPHICS_DESIGN = (6027, "Graphics & Design")
    HEALTH_FITNESS = (6013, "Health & Fitness")
    LIFESTYLE = (6012, "Lifestyle")
    MEDICAL = (6020, "Medical")
    MUSIC = (6011, "Music")
    NAVIGATION = (6010, "Navigation")
    NEWS = (6009, "News")
    NEWSSTAND = (6021, "Newsstand")
    PHOTO_VIDEO = (6008, "Photo & Video")
    PRODUCTIVITY = (6007, "Productivity")
    REFERENCE = (6006, "Reference")
    SOCIAL_NETWORKING = (6005, "Social Networking")
    SHOPPING = (6024, "Shopping")
    SPORTS = (6004, "Sports")
    TRAVEL = (6003, "Travel")
    UTILITIES = (6002, "Utilities")
    WEATHER = (6001, "Weather")

    def __new__(cls, code: int, name: str) -> Category:
        obj = object.__new__(cls)
        obj._value_ = code
        obj.display = name  # type: ignore
        return obj


# ------------------------------------------------------------------------------------------------ #
class DataType(Enum):
    APPDATA = "AppData"
    APPREVIEW = "AppReview"


# ------------------------------------------------------------------------------------------------ #
class StageType(Enum):
    EXTRACT = "Extract"
    TRANSFORM = "Transform"
    LOAD = "Load"


# ------------------------------------------------------------------------------------------------ #
class ProjectStatus(Enum):
    ACTIVE = "Active"
    IDLE = "Idle"


# ------------------------------------------------------------------------------------------------ #
class Status(Enum):
    CREATED = "Created"
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    ENDED = "Ended"
    COMPLETED = "Completed"


# ------------------------------------------------------------------------------------------------ #
class ProjectFrequency(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


# ------------------------------------------------------------------------------------------------ #
class Env(Enum):
    DEVELOPMENT = ("dev", "Development Environment")
    PRODUCTION = ("prod", "Production Environment")
    TEST = ("test", "Test Environment")

    def __new__(cls, value: str, description: str) -> Env:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description  # type: ignore
        return obj

    @classmethod
    def get(cls, value: str) -> Optional[Env]:
        for env in Env:
            if env.value == value:
                return env
        return None
