#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/content/appdata.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 12:47:38 am                                              #
# Modified   : Wednesday September 4th 2024 08:42:08 pm                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from appvocai.domain.content.base import Entity
from appvocai.toolkit.date import ThirdDateFormatter

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
dt_formatter = ThirdDateFormatter()


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppData(Entity):
    """
    A dataclass representing an application's data scraped from the App Store.

    Attributes:
        app_id (int): The unique identifier for the app. (Required)
        app_name (str): The name of the app. (Required)
        app_censored_name (str): The censored name of the app, as displayed in stores. (Required)
        bundle_id (str): The unique bundle identifier for the app. (Required)
        description (str): A description of the app. (Required)
        category_id (int): The ID of the primary category of the app. (Required)
        category (str): The name of the primary category of the app. (Required)
        categories (Optional[List[int]]): The list of categories to which the app is registered.
        price (float): The price of the app. Defaults to 0.
        currency (str): The currency in which the app's price is displayed. Defaults to "USD".
        rating_average (int): The average user rating for all versions of the app. (Required)
        rating_average_current_version (int): The average user rating for the current version of the app. (Required)
        rating_average_current_version_change (float): The change in average user rating during current version. Defaults to 0.
        rating_average_current_version_pct_change (float): The percent change in average user rating during current version. Defaults to 0.
        rating_count (int): The total number of user ratings for all versions. (Required)
        rating_count_current_version (int): The total number of user ratings for the current version. (Required)
        developer_id (int): The unique identifier for the app's developer. (Required)
        developer_name (str): The name of the app's developer. (Required)
        url_developer_view (Optional[str]): The URL to the developer's page on the App Store.
        seller_name (Optional[str]): The name of the seller or company behind the app.
        app_content_rating (Optional[str]): The content rating of the app.
        content_advisory_rating (Optional[str]): The advisory rating for the app's content.
        file_size_bytes (Optional[str]): The size of the app file in bytes.
        minimum_os_version (Optional[str]): The minimum OS version required to run the app.
        version (Optional[str]): The current version of the app.
        release_date (datetime): The release date of the app. (Required)
        release_notes (Optional[str]): The release notes for the current version of the app.
        release_date_current_version (datetime): The release date of the current version. (Required)
        iphone_support (bool): Whether the iPhone is a supported device. Default = True
        ipad_support (bool): Whether the iPad is a supported device. Default = True
        url_artwork_100 (Optional[str]): The URL for the 100px version of the app's artwork.
        url_app_view (Optional[str]): The URL to the app's page on the App Store.
        url_artwork_512 (Optional[str]): The URL for the 512px version of the app's artwork.
        url_artwork_60 (Optional[str]): The URL for the 60px version of the app's artwork.
        urls_screenshot_ipad (Optional[List[str]]): A list of URLs to the app's iPad screenshots.
        urls_screenshot (Optional[List[str]]): A list of URLs to the app's iPhone screenshots.
        extract_date (Optional[datetime]): The date the data was last extracted from the App Store.
    """

    app_id: int
    app_name: str
    app_censored_name: str
    bundle_id: str
    description: str
    category_id: int
    category: str
    rating_average: int
    rating_average_current_version: int
    rating_count: int
    rating_count_current_version: int
    developer_id: int
    developer_name: str
    release_date: datetime
    release_date_current_version: datetime
    categories: Optional[List[int]] = field(default_factory=lambda: None)
    price: float = 0
    currency: str = "USD"
    rating_average_current_version_change: float = 0
    rating_average_current_version_pct_change: float = 0
    seller_name: Optional[str] = None
    seller_url: Optional[str] = None
    app_content_rating: Optional[str] = None
    content_advisory_rating: Optional[str] = None
    file_size_bytes: Optional[str] = None
    minimum_os_version: Optional[str] = None
    version: Optional[str] = None
    release_notes: Optional[str] = None
    url_developer_view: Optional[str] = None
    url_app_view: Optional[str] = None
    url_artwork_100: Optional[str] = None
    url_artwork_512: Optional[str] = None
    url_artwork_60: Optional[str] = None
    urls_screenshot_ipad: Optional[List[str]] = field(default_factory=lambda: None)
    urls_screenshot: Optional[List[str]] = field(default_factory=lambda: None)
    iphone_support: bool = True
    ipad_support: bool = True

    extract_date: Optional[datetime] = None

    @classmethod
    def create(cls, appdata_row: Dict[str, Any], categories: List[int]) -> "AppData":
        """
        Creates an AppData object from the retrieved data.

        Args:
            appdata_row (Dict[str, Any]): A dictionary containing app data fields.
            categories (List[int]): A list of category IDs associated with the app.

        Returns:
            AppData: An instance of the AppData class populated with the provided data.

        Raises:
            ValueError: If any required field is missing or invalid.

        Logs:
            - Logs an error if a required field is missing.
            - Logs the successful creation of an AppData object.
        """
        # Required fields with their respective default values if missing
        required_fields = [
            "app_id",
            "app_name",
            "app_censored_name",
            "bundle_id",
            "description",
            "category_id",
            "category",
            "rating_average",
            "rating_average_current_version",
            "rating_count",
            "rating_count_current_version",
            "developer_id",
            "developer_name",
            "release_date",
            "release_date_current_version",
        ]

        # Check if any required field is missing or None
        missing_fields = [
            field for field in required_fields if not appdata_row.get(field)
        ]
        if missing_fields:
            msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.exception(msg)
            raise ValueError(msg)

        # Extract and validate data
        app_id = appdata_row["app_id"]
        logger.info(f"Creating AppData object for app_id: {app_id}")

        # Create the AppData object using the provided data
        app_data = cls(
            app_id=app_id,
            app_name=appdata_row["app_name"],
            app_censored_name=appdata_row["app_censored_name"],
            bundle_id=appdata_row["bundle_id"],
            description=appdata_row["description"],
            category_id=appdata_row["category_id"],
            category=appdata_row["category"],
            categories=categories,
            price=appdata_row.get("price", 0),
            currency=appdata_row.get("currency", "USD"),
            rating_average=appdata_row["rating_average"],
            rating_average_current_version=appdata_row[
                "rating_average_current_version"
            ],
            rating_average_current_version_change=appdata_row.get(
                "rating_average_current_version_change", 0
            ),
            rating_average_current_version_pct_change=appdata_row.get(
                "rating_average_current_version_pct_change", 0
            ),
            rating_count=appdata_row["rating_count"],
            rating_count_current_version=appdata_row["rating_count_current_version"],
            developer_id=appdata_row["developer_id"],
            developer_name=appdata_row["developer_name"],
            seller_name=appdata_row.get("seller_name"),
            seller_url=appdata_row.get("seller_url"),
            app_content_rating=appdata_row.get("app_content_rating"),
            content_advisory_rating=appdata_row.get("content_advisory_rating"),
            file_size_bytes=appdata_row.get("file_size_bytes"),
            minimum_os_version=appdata_row.get("minimum_os_version"),
            version=appdata_row.get("version"),
            release_date=dt_formatter.from_iso8601(appdata_row["release_date"]),
            release_notes=appdata_row.get("release_notes"),
            release_date_current_version=dt_formatter.from_iso8601(
                appdata_row["release_date_current_version"]
            ),
            url_developer_view=appdata_row.get("url_developer_view"),
            url_app_view=appdata_row.get("url_app_view"),
            url_artwork_100=appdata_row.get("url_artwork_100"),
            url_artwork_512=appdata_row.get("url_artwork_512"),
            url_artwork_60=appdata_row.get("url_artwork_60"),
            urls_screenshot_ipad=appdata_row.get("urls_screenshot_ipad"),
            urls_screenshot=appdata_row.get("urls_screenshot"),
            iphone_support=appdata_row.get("iphone_support", True),
            ipad_support=appdata_row.get("ipad_support", True),
            extract_date=dt_formatter.from_iso8601(appdata_row["extract_date"]),
        )

        # Log the successful creation of an AppData object
        logger.info(f"Successfully created AppData object for app_id: {app_id}")
        return app_data

    def export_appdata(self) -> Dict[str, Any]:
        """
        Exports the app's data for insertion into the appdata table.

        Returns:
            Dict[str, any]: A dictionary containing key-value pairs representing columns in the appdata table.
        """
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "app_censored_name": self.app_censored_name,
            "bundle_id": self.bundle_id,
            "description": self.description,
            "category_id": self.category_id,
            "category": self.category,
            "price": self.price,
            "currency": self.currency,
            "rating_average": self.rating_average,
            "rating_average_current_version": self.rating_average_current_version,
            "rating_average_current_version_change": self.rating_average_current_version_change,
            "rating_average_current_version_pct_change": self.rating_average_current_version_pct_change,
            "rating_count": self.rating_count,
            "rating_count_current_version": self.rating_average_current_version,
            "developer_id": self.developer_id,
            "developer_name": self.developer_name,
            "seller_name": self.seller_name,
            "seller_url": self.seller_url,
            "app_content_rating": self.app_content_rating,
            "content_advisory_rating": self.content_advisory_rating,
            "file_size_bytes": self.file_size_bytes,
            "minimum_os_version": self.minimum_os_version,
            "version": self.version,
            "release_date": self.release_date,
            "release_notes": self.release_notes,
            "release_date_current_version": self.release_date_current_version,
            "url_developer_view": self.url_developer_view,
            "url_app_view": self.url_app_view,
            "url_artwork_100": self.url_artwork_100,
            "url_artwork_512": self.url_artwork_512,
            "url_artwork_60": self.url_artwork_60,
            "urls_screenshot_ipad": self.urls_screenshot_ipad,
            "urls_screenshot": self.urls_screenshot,
            "extract_date": self.extract_date,
        }

    def export_categories(self) -> List[Dict[str, int]]:
        """
        Exports the app's category IDs for insertion into the categories table.

        Returns:
            List[Dict[int, int]]: A list of dictionaries, each representing a category record with app_id and category_id.
        """
        if self.categories:
            return [
                {"app_id": self.app_id, "category_id": category_id}
                for category_id in self.categories
            ]
        else:
            return []


# ------------------------------------------------------------------------------------------------ #
#                                     RAW APPDATA                                                  #
# ------------------------------------------------------------------------------------------------ #
class RawAppData(BaseModel):
    """
    A dataclass representing an application's data scraped from the App Store.
    """

    app_id: int = Field(...)
    app_name: str = Field(..., min_length=1)
    app_censored_name: str = Field(...)
    bundle_id: str = Field(...)
    description: str = Field(..., min_length=1)
    category_id: int = Field(...)
    category: str = Field(...)
    rating_average: int = Field(..., ge=0, le=5)
    rating_average_current_version: int = Field(..., ge=0, le=5)
    rating_count: int = Field(..., ge=0)
    rating_count_current_version: int = Field(0, ge=0)
    developer_id: int = Field(...)
    developer_name: str = Field(...)
    release_date: datetime
    release_date_current_version: datetime
    price: float = Field(0.0, ge=0.0)
    currency: str = Field("USD", min_length=3, max_length=3)
    categories: Optional[List[int]] = field(default_factory=lambda: None)
    seller_name: Optional[str] = None
    seller_url: Optional[str] = None
    app_content_rating: Optional[str] = None
    content_advisory_rating: Optional[str] = None
    file_size_bytes: Optional[str] = None
    minimum_os_version: Optional[str] = None
    version: Optional[str] = None
    release_notes: Optional[str] = None
    url_developer_view: Optional[str] = None
    url_app_view: Optional[str] = None
    url_artwork_100: Optional[str] = None
    url_artwork_512: Optional[str] = None
    url_artwork_60: Optional[str] = None
    urls_screenshot_ipad: Optional[List[str]] = field(default_factory=lambda: None)
    urls_screenshot: Optional[List[str]] = field(default_factory=lambda: None)
    supported_devices: Optional[List[str]] = field(default_factory=lambda: None)

    @classmethod
    def create(cls, content: Dict[str, Any]) -> RawAppData:
        return cls(
            app_id=content["trackId"],
            app_name=content["trackName"],
            app_censored_name=content["trackCensoredName"],
            bundle_id=content["bundleId"],
            description=content["description"],
            category_id=content["primaryGenreId"],
            category=content["primaryGenreName"],
            price=content["price"],
            currency=content["currency"],
            rating_average=content["averageUserRating"],
            rating_average_current_version=content[
                "averageUserRatingForCurrentVersion"
            ],
            rating_count=content["userRatingCount"],
            rating_count_current_version=content["userRatingCountForCurrentVersion"],
            developer_id=content["artistId"],
            developer_name=content["artistName"],
            release_date=dt_formatter.from_iso8601(content["releaseDate"]),
            release_date_current_version=dt_formatter.from_iso8601(
                content["currentVersionReleaseDate"]
            ),
            categories=content.get("genreIds"),
            url_developer_view=content.get("artistViewUrl"),
            seller_name=content.get("sellerName"),
            seller_url=content.get("sellerUrl"),
            app_content_rating=content.get("trackContentRating"),
            content_advisory_rating=content.get("contentAdvisoryRating"),
            file_size_bytes=content.get("fileSizeBytes"),
            minimum_os_version=content.get("minimumOsVersion"),
            version=content.get("version"),
            release_notes=content.get("releaseNotes"),
            url_artwork_100=content.get("artworkUrl100"),
            url_app_view=content.get("trackViewUrl"),
            url_artwork_512=content.get("artworkUrl512"),
            url_artwork_60=content.get("artworkUrl60"),
            urls_screenshot_ipad=content.get("ipadScreenshotUrls"),
            urls_screenshot=content.get("screenshotUrls"),
            supported_devices=content.get("supportedDevices", []),
        )
