#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/appdata/response.py                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 05:53:12 am                                                   #
# Modified   : Sunday July 28th 2024 05:19:24 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Response Module"""
import logging
from dataclasses import dataclass
from datetime import datetime

from appstorestream.application.base.response import AsyncResponse

# ------------------------------------------------------------------------------------------------ #

@dataclass
class AppDataAsyncResponse(AsyncResponse):

    def parse_results(self, results: list) ->None:
        """Parse the results into a list of dictionaries."""

        for result in results:

            try:

                if 'error' in result.keys():
                    self.log_error(result['error'])
                else:
                    self.response_count += 1
                    for record in result['results']:
                        self.record_count += 1
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
                        appdata["rating_average_current_version"] = record["averageUserRatingForCurrentVersion"]
                        appdata["rating_average_current_version_change"] = appdata["rating_average_current_version"] - appdata["rating_average"]
                        appdata["rating_average_current_version_pct_change"] = appdata["rating_average_current_version_change"] /  appdata["rating_average"] * 100
                        appdata["rating_count"] = record["userRatingCount"]
                        appdata["rating_count_current_version"] = record["userRatingCountForCurrentVersion"]
                        appdata["release_date"] = datetime.strptime(
                            record["releaseDate"], "%Y-%m-%dT%H:%M:%f%z"
                        )
                        appdata["release_date_current_version"] = datetime.strptime(
                            record["currentVersionReleaseDate"], "%Y-%m-%dT%H:%M:%f%z"
                        )

                        appdata["software_lifecycle_duration"] = (appdata["release_date_current_version"] - appdata["release_date"]).days
                        appdata["days_since_release"] = (datetime.now() - appdata["release_date"]).days
                        appdata["days_since_current_version"] = (datetime.now() - appdata["release_date_current_version"]).days

                        appdata["rating_count_per_day"] = appdata["rating_count"] / appdata["days_since_release"]
                        appdata["rating_count_per_day_current_version"] = appdata["rating_count_current_version"] / appdata["days_since_current_version"]
                        appdata["rating_count_per_day_current_version_pct_change"] = (appdata["rating_count_per_day_current_version"] - appdata["rating_count_per_day"]) / appdata["rating_count_per_day"] * 100

                        appdata["app_version"] = record["version"]
                        appdata["extract_date"] = datetime.now()

                        try:
                            # Optional fields
                            appdata["developer_url"] = record["artistViewUrl"]
                            appdata["seller_url"] = record["sellerUrl"]
                            appdata["app_url"] = record["trackViewUrl"]
                            appdata["screenshot_urls"] = {"screenshot_urls": record["screenshotUrls"],"screenshot_urls_ipad":record["ipadScreenshotUrls"]}
                        except KeyError:
                            pass

                        self.content.append(appdata)

            except Exception as e:
                logger = self.get_logger()
                logger.warning(f"Unknown exception occurred:\{e}")
                pass