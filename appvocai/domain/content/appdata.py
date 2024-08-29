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
# Modified   : Thursday August 29th 2024 04:47:43 pm                                               #
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
        price (Optional[float]): The price of the app.
        currency (Optional[str]): The currency in which the app's price is displayed.
        average_user_rating (Optional[int]): The average user rating for all versions of the app.
        average_user_rating_current_version (Optional[int]): The average user rating for the current version of the app.
        user_rating_count (Optional[int]): The total number of user ratings for all versions.
        user_rating_current_version (Optional[int]): The total number of user ratings for the current version.
        developer_id (Optional[int]): The unique identifier for the app's developer.
        developer_name (Optional[str]): The name of the app's developer.
        developer_view_url (Optional[str]): The URL to the developer's page on the App Store.
        seller_name (Optional[str]): The name of the seller or company behind the app.
        seller_url (Optional[str]): The URL to the seller's website.
        app_content_rating (Optional[str]): The content rating of the app.
        content_advisory_rating (Optional[str]): The advisory rating for the app's content.
        file_size_bytes (Optional[str]): The size of the app file in bytes.
        minimum_os_version (Optional[str]): The minimum OS version required to run the app.
        version (Optional[str]): The current version of the app.
        release_date (Optional[datetime]): The release date of the app.
        release_notes (Optional[str]): The release notes for the current version of the app.
        current_version_release_date (Optional[datetime]): The release date of the current version.
        artwork_url100 (Optional[str]): The URL for the 100px version of the app's artwork.
        app_view_url (Optional[str]): The URL to the app's page on the App Store.
        artwork_url512 (Optional[str]): The URL for the 512px version of the app's artwork.
        artwork_url60 (Optional[str]): The URL for the 60px version of the app's artwork.
        extract_date (Optional[datetime]): The date the data was last extracted from the App Store.
    """

    app_id: int
    app_name: str
    app_censored_name: str
    bundle_id: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    average_user_rating: Optional[int] = None
    average_user_rating_current_version: Optional[int] = None
    user_rating_count: Optional[int] = None
    user_rating_current_version: Optional[int] = None
    developer_id: Optional[int] = None
    developer_name: Optional[str] = None
    developer_view_url: Optional[str] = None
    seller_name: Optional[str] = None
    seller_url: Optional[str] = None
    app_content_rating: Optional[str] = None
    content_advisory_rating: Optional[str] = None
    file_size_bytes: Optional[str] = None
    minimum_os_version: Optional[str] = None
    version: Optional[str] = None
    release_date: Optional[datetime] = None
    release_notes: Optional[str] = None
    current_version_release_date: Optional[datetime] = None
    artwork_url100: Optional[str] = None
    app_view_url: Optional[str] = None
    artwork_url512: Optional[str] = None
    artwork_url60: Optional[str] = None
    extract_date: Optional[datetime] = None

    categories: List[int] = field(default_factory=list)
    ipad_screenshot_urls: List[str] = field(default_factory=list)
    screenshot_urls: List[str] = field(default_factory=list)

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
            "average_user_rating": self.average_user_rating,
            "average_user_rating_current_version": self.average_user_rating_current_version,
            "user_rating_count": self.user_rating_count,
            "user_rating_current_version": self.user_rating_current_version,
            "developer_id": self.developer_id,
            "developer_name": self.developer_name,
            "developer_view_url": self.developer_view_url,
            "seller_name": self.seller_name,
            "seller_url": self.seller_url,
            "app_content_rating": self.app_content_rating,
            "content_advisory_rating": self.content_advisory_rating,
            "file_size_bytes": self.file_size_bytes,
            "minimum_os_version": self.minimum_os_version,
            "version": self.version,
            "release_date": self.release_date,
            "release_notes": self.release_notes,
            "current_version_release_date": self.current_version_release_date,
            "artwork_url100": self.artwork_url100,
            "app_view_url": self.app_view_url,
            "artwork_url512": self.artwork_url512,
            "artwork_url60": self.artwork_url60,
            "extract_date": self.extract_date
        }

    def export_urls(self) -> List[Dict[str, Any]]:
        """
        Exports the app's URLs for insertion into the urls table.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each representing a URL record with app_id, url, and url_type.
        """
        urls = []
        for url in self.ipad_screenshot_urls:
            urls.append({
                "app_id": self.app_id,
                "url": url,
                "url_type": "ipad"
            })
        for url in self.screenshot_urls:
            urls.append({
                "app_id": self.app_id,
                "url": url,
                "url_type": "screenshot"
            })
        return urls

    def export_categories(self) -> List[Dict[str, int]]:
        """
        Exports the app's category IDs for insertion into the categories table.

        Returns:
            List[Dict[int, int]]: A list of dictionaries, each representing a category record with app_id and category_id.
        """
        return [{"app_id": self.app_id, "category_id": category_id} for category_id in self.categories]


