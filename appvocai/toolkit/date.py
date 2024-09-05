#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/toolkit/date.py                                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 04:54:23 pm                                              #
# Modified   : Thursday September 5th 2024 06:44:56 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import pytz


# ------------------------------------------------------------------------------------------------ #
class TimePrecision(Enum):
    """
    Enumeration for time precision levels in ISO 8601 formatting.

    Attributes:
        MINUTES: Represents time precision up to minutes.
        SECONDS: Represents time precision up to seconds.
        MILLISECONDS: Represents time precision up to milliseconds.
        MICROSECONDS: Represents time precision up to microseconds.
    """

    MINUTES = "minutes"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"


class ThirdDateFormatter:
    """
    A utility class for formatting and converting datetime objects.

    Methods:
        to_iso8601_format(dt: datetime, precision: TimePrecision = TimePrecision.SECONDS) -> str:
            Converts a datetime object to ISO 8601 format with the specified precision.

        to_HTTP_format(dt: datetime) -> str:
            Converts a datetime object to HTTP date format.

        to_utc_datetime(dt: datetime, local_tz: Optional[str] = None) -> datetime:
            Converts a given datetime to UTC. Handles both naive and timezone-aware datetimes.

        from_iso8601(dt_string: str) -> datetime:
            Parses an ISO 8601 formatted string into a datetime object.

        format_duration(seconds: float) -> str:
            Converts a duration in seconds to a human-readable string format.
    """

    def to_iso8601_format(
        self, dt: datetime, precision: TimePrecision = TimePrecision.SECONDS
    ) -> str:
        """
        Converts a datetime object to ISO 8601 format with the specified precision.

        Parameters:
            dt (datetime): The datetime object to format.
            precision (TimePrecision): The precision level for formatting (default is seconds).

        Returns:
            str: The formatted datetime string in ISO 8601 format.
        """
        return dt.isoformat(sep="T", timespec=precision.value) + "Z"

    def to_HTTP_format(self, dt: datetime) -> str:
        """
        Converts a datetime object to HTTP date format.

        Parameters:
            dt (datetime): The datetime object to format.

        Returns:
            str: The formatted datetime string in HTTP date format.
        """
        return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def to_utc_datetime(self, dt: datetime, local_tz: Optional[str] = None) -> datetime:
        """
        Converts a given datetime to UTC. Handles both naive and timezone-aware datetimes.

        Parameters:
            dt (datetime): The datetime object to convert.
            local_tz (str, optional): The local timezone name if the datetime is naive. Defaults to None.

        Returns:
            datetime: The converted datetime object in UTC.
        """
        if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) == timezone.utc.utcoffset(
            dt
        ):
            return dt  # Return the datetime as-is if it's already in UTC

        if dt.tzinfo is None:  # If naive datetime (no timezone info)
            if local_tz:
                local_timezone = pytz.timezone(local_tz)
                dt = local_timezone.localize(dt)  # Localize naive datetime
            else:
                dt = dt.replace(
                    tzinfo=timezone.utc
                )  # Assume as UTC if no timezone is provided

        return dt.astimezone()  # Convert to UTC if it's in a different timezone

    def from_iso8601(self, dt_string: str) -> datetime:
        """
        Parses an ISO 8601 formatted string into a datetime object.

        Parameters:
            dt_string (str): The ISO 8601 formatted datetime string.

        Returns:
            datetime: The parsed datetime object.
        """
        return datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%SZ")

    def format_duration(self, seconds: float) -> str:
        """
        Converts a duration in seconds to a human-readable string format of minutes or hours and minutes.

        Parameters:
            seconds (float): The duration in seconds to format.

        Returns:
            str: A string representation of the duration.
        """
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes} minutes" + (
                f" and {remaining_seconds} seconds" if remaining_seconds > 0 else ""
            )
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            remaining_seconds = seconds % 60
            return (
                f"{hours} hours"
                + (f" {minutes} minutes" if minutes > 0 else "")
                + (
                    f" and {round(remaining_seconds, 2)} seconds"
                    if remaining_seconds > 0
                    else ""
                )
            )
