#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/appdata/response.py                                          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 05:53:12 am                                                   #
# Modified   : Sunday August 25th 2024 12:11:47 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Response Module"""
import logging
from dataclasses import dataclass
from datetime import datetime

from pytz import timezone

from appstorestream.domain.base.response import AsyncResponse

# ------------------------------------------------------------------------------------------------ #
# mypy: ignore_errors
# ------------------------------------------------------------------------------------------------ #
tz = timezone("EST")
# ------------------------------------------------------------------------------------------------ #


class AppDataResponse(AsyncResponse):

    def parse_results(self) -> None:
        """Parse the results into a list of dictionaries."""

        # Get timezone aware current datetime.
        current_dt = datetime.now(tz)

        for result in self._results:
            try:
                for record in result["results"]:

                    appdata = {}
                    # required fields
                    appdata["app_id"] = record["trackId"]
                    appdata["app_name"] = record["trackName"]
                    appdata["app_description"] = record["description"].strip()
                    appdata["category_id"] = record["primaryGenreId"]
                    appdata["category"] = record["primaryGenreName"]
                    appdata["developer_id"] = record["artistId"]
                    appdata["developer"] = record["artistName"]
                    appdata["seller_name"] = record["sellerName"]
                    appdata["price"] = record.get("price", 0)
                    appdata["rating_average"] = record["averageUserRating"]
                    appdata["rating_average_current_version"] = record[
                        "averageUserRatingForCurrentVersion"
                    ]
                    appdata["rating_average_current_version_change"] = (
                        appdata["rating_average_current_version"]
                        - appdata["rating_average"]
                    )
                    appdata["rating_average_current_version_pct_change"] = (
                        (
                            appdata["rating_average_current_version_change"]
                            / appdata["rating_average"]
                            * 100
                        )
                        if appdata["rating_average"] > 0
                        else 0
                    )
                    appdata["rating_count"] = record["userRatingCount"]
                    appdata["rating_count_current_version"] = record[
                        "userRatingCountForCurrentVersion"
                    ]
                    appdata["release_date"] = datetime.strptime(
                        record["releaseDate"], "%Y-%m-%dT%H:%M:%f%z"
                    )
                    appdata["release_date_current_version"] = datetime.strptime(
                        record["currentVersionReleaseDate"], "%Y-%m-%dT%H:%M:%f%z"
                    )

                    appdata["software_lifecycle_response_time"] = (
                        appdata["release_date_current_version"]
                        - appdata["release_date"]
                    ).days
                    appdata["days_since_release"] = (
                        current_dt - appdata["release_date"]
                    ).days
                    appdata["days_since_current_version"] = (
                        current_dt - appdata["release_date_current_version"]
                    ).days

                    appdata["rating_count_per_day"] = (
                        appdata["rating_count"] / appdata["days_since_release"]
                        if appdata["days_since_release"] > 0
                        else 0
                    )
                    appdata["rating_count_per_day_current_version"] = (
                        appdata["rating_count_current_version"]
                        / appdata["days_since_current_version"]
                        if appdata["days_since_current_version"] > 0
                        else 0
                    )
                    appdata["rating_count_per_day_current_version_pct_change"] = (
                        (
                            appdata["rating_count_per_day_current_version"]
                            - appdata["rating_count_per_day"]
                        )
                        / appdata["rating_count_per_day"]
                        * 100
                        if appdata["rating_count_per_day"] > 0
                        else 0
                    )

                    appdata["app_version"] = record["version"]
                    appdata["extract_date"] = current_dt

                    try:
                        # Optional fields
                        appdata["developer_url"] = record["artistViewUrl"]
                        appdata["seller_url"] = record["sellerUrl"]
                        appdata["app_url"] = record["trackViewUrl"]
                        appdata["screenshot_urls"] = {
                            "screenshot_urls": record["screenshotUrls"],
                            "screenshot_urls_ipad": record["ipadScreenshotUrls"],
                        }
                    except KeyError:
                        pass

                    self._content.append(appdata)

            except Exception as e:
                logging.warning(f"Unknown exception occurred:\n{e}")
