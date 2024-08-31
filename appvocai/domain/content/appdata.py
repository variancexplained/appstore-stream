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
# Modified   : Friday August 30th 2024 02:13:14 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from appvocai.core.data import DataClass


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


