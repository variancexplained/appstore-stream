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
# Modified   : Saturday August 31st 2024 05:17:20 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from appvocai.core.data import DataClass

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppData(DataClass):
    """
    A dataclass representing an application's data scraped from the App Store.

    Attributes:
        app_id (int): The unique identifier for the app.
        app_name (str): The name of the app.
        app_censored_name (str): The censored name of the app, as displayed in stores.
        bundle_id (str): The unique bundle identifier for the app.
        description (Optional[str]): A description of the app.
        category_id (Optional[int]): The ID of the primary category of the app.
        category (Optional[str]): The name of the primary category of the app.
        categories (Optional[List[int]]): The list of categories to which the app is registered.
        price (Optional[float]): The price of the app.
        currency (Optional[str]): The currency in which the app's price is displayed.
        rating_average (Optional[int]): The average user rating for all versions of the app.
        rating_average_current_version (Optional[int]): The average user rating for the current version of the app.
        rating_average_current_version_change (Optional[float]): The change in average user rating during current version.
        rating_average_current_version_pct_change (Optional[float]): The percent change in average user rating during current version.
        rating_count (Optional[int]): The total number of user ratings for all versions.
        rating_count_current_version (Optional[int]): The total number of user ratings for the current version.
        developer_id (Optional[int]): The unique identifier for the app's developer.
        developer_name (Optional[str]): The name of the app's developer.
        url_developer_view (Optional[str]): The URL to the developer's page on the App Store.
        seller_name (Optional[str]): The name of the seller or company behind the app.
        url_seller (Optional[str]): The URL to the seller's website.
        app_content_rating (Optional[str]): The content rating of the app.
        content_advisory_rating (Optional[str]): The advisory rating for the app's content.
        file_size_bytes (Optional[str]): The size of the app file in bytes.
        minimum_os_version (Optional[str]): The minimum OS version required to run the app.
        version (Optional[str]): The current version of the app.
        release_date (Optional[datetime]): The release date of the app.
        release_notes (Optional[str]): The release notes for the current version of the app.
        release_date_current_version (Optional[datetime]): The release date of the current version.
        url_artwork_100 (Optional[str]): The URL for the 100px version of the app's artwork.
        url_app_view (Optional[str]): The URL to the app's page on the App Store.
        url_artwork_512 (Optional[str]): The URL for the 512px version of the app's artwork.
        url_artwork_60 (Optional[str]): The URL for the 60px version of the app's artwork.
        urls_screenshot_ipad (Optional[List[str]]): A list of URLS to the app's ipad screenshots.
        urls_screenshot_iphone (Optional[List[str]]): A list of URLS to the app's iphone screenshots.
        extract_date (Optional[datetime]): The date the data was last extracted from the App Store.
    """

    app_id: int
    app_name: str
    app_censored_name: str
    bundle_id: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[str] = None
    categories: Optional[List[int]] = field(default_factory=lambda: None)
    price: Optional[float] = None
    currency: Optional[str] = None
    rating_average: Optional[int] = None
    rating_average_current_version: Optional[int] = None
    rating_average_current_version_change: Optional[float] = None
    rating_average_current_version_pct_change: Optional[float] = None
    rating_count: Optional[int] = None
    rating_count_current_version: Optional[int] = None
    developer_id: Optional[int] = None
    developer_name: Optional[str] = None
    seller_name: Optional[str] = None
    app_content_rating: Optional[str] = None
    content_advisory_rating: Optional[str] = None
    file_size_bytes: Optional[str] = None
    minimum_os_version: Optional[str] = None
    version: Optional[str] = None
    release_date: Optional[datetime] = None
    release_notes: Optional[str] = None
    release_date_current_version: Optional[datetime] = None
    url_developer_view: Optional[str] = None
    url_seller: Optional[str] = None
    url_app_view: Optional[str] = None
    url_artwork_100: Optional[str] = None
    url_artwork_512: Optional[str] = None
    url_artwork_60: Optional[str] = None
    urls_screenshot_ipad: Optional[List[str]] = field(default_factory=lambda: None)
    urls_screenshot_iphone: Optional[List[str]] = field(default_factory=lambda: None)
    extract_date: Optional[datetime] = None


    @classmethod
    def create(cls, appdata_row: Dict[str, Any], categories: List[int]) -> AppData:
        """Create an AppData object from the retrieved data.

        Args:
            appdata_row (Dict[str, Any]): A dictionary containing app data fields.
            categories (List[int]): A list of category IDs associated with the app.

        Returns:
            AppData: An instance of the AppData class populated with the provided data.

        Raises:
            ValueError: If app_id is None or if any required field is missing.

        Logs:
            - Logs an error if app_id is None.
            - Logs the successful creation of an AppData object.
        """
        app_id = appdata_row.get('app_id')
        if app_id is None:
            msg = "app_id cannot be None"
            logger.exception(msg)
            raise ValueError(msg)

        # Use default values for optional fields
        app_name = appdata_row.get('app_name', "Unknown")
        app_censored_name = appdata_row.get('app_censored_name', "Unknown")
        bundle_id = appdata_row.get('bundle_id', "Unknown")


        # Log the successful creation of an AppData object
        return cls(
            app_id=app_id,
            app_name=app_name,
            app_censored_name=app_censored_name,
            bundle_id=bundle_id,
            description=appdata_row.get('description'),
            category_id=appdata_row.get('category_id'),
            category=appdata_row.get('category'),
            categories=categories,
            price=appdata_row.get('price'),
            currency=appdata_row.get('currency'),
            rating_average=appdata_row.get('rating_average'),
            rating_average_current_version=appdata_row.get('rating_average_current_version'),
            rating_average_current_version_change=appdata_row.get('rating_average_current_version_change'),
            rating_average_current_version_pct_change=appdata_row.get('rating_average_current_version_pct_change'),
            rating_count=appdata_row.get('rating_count'),
            rating_count_current_version=appdata_row.get('rating_count_current_version'),
            developer_id=appdata_row.get('developer_id'),
            developer_name=appdata_row.get('developer_name'),
            seller_name=appdata_row.get('seller_name'),
            app_content_rating=appdata_row.get('app_content_rating'),
            content_advisory_rating=appdata_row.get('content_advisory_rating'),
            file_size_bytes=appdata_row.get('file_size_bytes'),
            minimum_os_version=appdata_row.get('minimum_os_version'),
            version=appdata_row.get('version'),
            release_date=appdata_row.get('release_date'),
            release_notes=appdata_row.get('release_notes'),
            release_date_current_version=appdata_row.get('release_date_current_version'),
            url_developer_view=appdata_row.get('url_developer_view'),
            url_seller=appdata_row.get('url_seller'),
            url_app_view=appdata_row.get('url_app_view'),
            url_artwork_100=appdata_row.get('url_artwork_100'),
            url_artwork_512=appdata_row.get('url_artwork_512'),
            url_artwork_60=appdata_row.get('url_artwork_60'),
            extract_date=appdata_row.get('extract_date'),
            urls_screenshot_ipad=appdata_row.get("urls_screenshot_ipad"),
            urls_screenshot_iphone=appdata_row.get("urls_screenshot_iphone"),
        )


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
            "app_content_rating": self.app_content_rating,
            "content_advisory_rating": self.content_advisory_rating,
            "file_size_bytes": self.file_size_bytes,
            "minimum_os_version": self.minimum_os_version,
            "version": self.version,
            "release_date": self.release_date,
            "release_notes": self.release_notes,
            "release_date_current_version": self.release_date_current_version,
            "url_developer_view": self.url_developer_view,
            "url_seller": self.url_seller,
            "url_app_view": self.url_app_view,
            "url_artwork_100": self.url_artwork_100,
            "url_artwork_512": self.url_artwork_512,
            "url_artwork_60": self.url_artwork_60,
            "urls_screenshot_ipad": self.urls_screenshot_ipad,
            "urls_screenshot_iphone": self.urls_screenshot_iphone,
            "extract_date": self.extract_date
        }

    def export_categories(self) -> List[Dict[str, int]]:
        """
        Exports the app's category IDs for insertion into the categories table.

        Returns:
            List[Dict[int, int]]: A list of dictionaries, each representing a category record with app_id and category_id.
        """
        if self.categories:
            return [{"app_id": self.app_id, "category_id": category_id} for category_id in self.categories]
        else:
            return []


