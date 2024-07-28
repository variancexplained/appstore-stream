#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/appdata/extract/response.py                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 05:53:12 am                                                   #
# Modified   : Friday July 26th 2024 11:34:50 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Response Module"""
import logging
from dataclasses import dataclass
from datetime import datetime

from appstorestream.application.response import AsyncResponse

# ------------------------------------------------------------------------------------------------ #

@dataclass
class AppDataAsyncResponse(AsyncResponse):

    def parse_response(self, response: list) ->None:
        """Parse the response into a list of dictionaries."""
        try:

            for response in self._response:

                for result in response['results']:
                    appdata = {}
                    # required fields
                    appdata["id"] = result["trackId"]
                    appdata["name"] = result["trackName"]
                    appdata["description"] = result["description"].strip()
                    appdata["category_id"] = result["primaryGenreId"]
                    appdata["category"] = result["primaryGenreName"]
                    appdata["developer_id"] = result["artistId"]
                    appdata["developer"] = result["artistName"]
                    appdata["seller_name"] = result["sellerName"]
                    appdata["seller_url"] = result["sellerUrl"]
                    appdata["price"] = result.get("price", 0)
                    appdata["rating_average"] = result["averageUserRating"]
                    appdata["rating_average_current_version"] = result["averageUserRatingForCurrentVersion"]
                    appdata["rating_count"] = result["userRatingCount"]
                    appdata["rating_count_current_version"] = result["userRatingCountForCurrentVersion"]
                    appdata["release_date"] = datetime.strptime(
                        result["releaseDate"], "%Y-%m-%dT%H:%M:%f%z"
                    )
                    appdata["release_date_current_version"] = datetime.strptime(
                        result["currentVersionReleaseDate"], "%Y-%m-%dT%H:%M:%f%z"
                    )
                    appdata["version"] = result["version"]
                    appdata["extract_date"] = datetime.now()

                    try:
                        # Optional fields
                        appdata["developer_url"] = result["artistViewUrl"]
                        appdata["app_url"] = result["trackViewUrl"]
                        appdata["screenshot_urls"] = {"screenshot_urls": result["screenshotUrls"],"screenshot_urls_ipad":result["ipadScreenshotUrls"]}
                    except KeyError:
                        pass

                    self.content.append(appdata)
        except Exception:
            """A Data Error has occurred."""
            self.data_errors += 1
            self.total_errors += 1
            logging.warning(
                        f"An data error has ucurred."
                    )
