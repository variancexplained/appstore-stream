#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/core/date_time.py                                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 04:54:23 pm                                              #
# Modified   : Wednesday August 28th 2024 09:30:03 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #

from datetime import datetime, timezone
from typing import Optional

import pytz


# ------------------------------------------------------------------------------------------------ #
def to_utc(dt: datetime, local_tz: Optional[str] = None) -> datetime:
    """
    Converts a given datetime to UTC.

    Parameters:
        dt (datetime): The datetime to convert.
        local_tz (str, optional): The local timezone name if the datetime is naive.

    Returns:
        datetime: The converted datetime in UTC.
    """
    # Check if the datetime is already in UTC
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) == timezone.utc.utcoffset(dt):
        return dt  # Return the datetime as-is if it's already in UTC

    if dt.tzinfo is None:  # If naive datetime (no timezone info)
        if local_tz:
            # Localize using the specified local timezone
            local_timezone = pytz.timezone(local_tz)
            dt = local_timezone.localize(dt)  # Localize naive datetime
        else:
            # If no timezone provided, assume it as UTC
            dt = dt.replace(tzinfo=timezone.utc)

    # Convert to UTC if it's in a different timezone
    return dt.astimezone(timezone.utc)


# ------------------------------------------------------------------------------------------------ #
def format_duration(seconds: float) -> str:
    """Convert seconds to a human-readable string format of minutes or hours and minutes.

    Args:
        seconds (int): The number of seconds to convert.

    Returns:
        str: A string representation of the duration.
    """
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes} minutes" + (f" and {remaining_seconds} seconds" if remaining_seconds > 0 else "")
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hours" + (f" and {minutes} minutes" if minutes > 0 else "")

