#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/repo/appdata.py                                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 10:27:12 pm                                                 #
# Modified   : Thursday August 29th 2024 09:08:27 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import logging
from typing import Any, Dict, List

import pandas as pd

from appvocai.core.enum import AppDataURLType, Category
from appvocai.domain.content.appdata import AppData
from appvocai.domain.repo.base import Repo
from appvocai.infra.database.mysql import MySQLDatabase

# ------------------------------------------------------------------------------------------------ #

class AppDataRepo(Repo):
    """
    Repository for managing app data, including retrieval and upsertion
    of app-related information from a MySQL database.

    Attributes:
        database (MySQLDatabase): The database connection instance.
        logger (logging.Logger): Logger for recording operational messages.
    """

    def __init__(self, database: MySQLDatabase) -> None:
        """Initializes the AppDataRepo with a given database instance.

        Args:
            database (MySQLDatabase): The database connection instance.
        """
        super().__init__()
        self._database = database
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_appdata(self, id_value: int) -> Dict[str, Any]:
        """Retrieve a single app's data from the appdata table.

        Args:
            id_value (int): The unique identifier for the app.

        Returns:
            Dict[str, Any]: A dictionary representing the app's data, or an empty
            dictionary if no data is found.
        """
        query = """
        SELECT * FROM appdata
        WHERE app_id = :app_id
        """
        params = {"app_id": id_value}

        result = self._database.execute(query=query, params=params)
        row = result.fetchone()  # Fetch the first row
        return dict(row) if row else {}

    def get_categories(self, id_value: int) -> List[int]:
        """Retrieve the categories associated with a specific app.

        Args:
            id_value (int): The unique identifier for the app.

        Returns:
            List[int]: A list of category IDs associated with the app.
        """
        query = """
        SELECT category_id FROM category_app
        WHERE app_id = :app_id
        """
        params = {"app_id": id_value}

        result = self._database.execute(query=query, params=params)
        rows = result.fetchall()  # Fetch all rows
        return [row.category_id for row in rows]

    def get_urls(self, id_value: int) -> List[Dict[str, str]]:
        """Retrieve URLs associated with a specific app.

        Args:
            id_value (int): The unique identifier for the app.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing URL types and URLs.
        """
        query = """
        SELECT url_type, url FROM app_url
        WHERE app_id = :app_id
        """
        params = {"app_id": id_value}

        result = self._database.execute(query=query, params=params)
        rows = result.fetchall()  # Fetch all rows
        return [dict(row) for row in rows]


    def constitute_appdata(
        self, appdata_row: Dict[str, Any], categories: List[int], urls: List[Dict[str, str]]
    ) -> AppData:
        """Create an AppData object from the retrieved data.

        Args:
            appdata_row (Dict[str, Any]): A dictionary containing app data fields.
            categories (List[int]): A list of category IDs associated with the app.
            urls (List[Dict[str, str]]): A list of dictionaries containing URLs and their types.

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
            self._logger.exception(msg)
            raise ValueError(msg)

        # Use default values for optional fields
        app_name = appdata_row.get('app_name', "Unknown")
        app_censored_name = appdata_row.get('app_censored_name', "Unknown")
        bundle_id = appdata_row.get('bundle_id', "Unknown")

        # Extract URL lists based on type
        ipad_screenshot_urls = [url['url'] for url in urls if url['url_type'] == AppDataURLType.IPAD.value]
        screenshot_urls = [url['url'] for url in urls if url['url_type'] == AppDataURLType.SCREENSHOT.value]

        # Log the successful creation of an AppData object
        app_data = AppData(
            app_id=app_id,
            app_name=app_name,
            app_censored_name=app_censored_name,
            bundle_id=bundle_id,
            description=appdata_row.get('description'),
            category_id=appdata_row.get('category_id'),
            category=appdata_row.get('category'),
            price=appdata_row.get('price'),
            currency=appdata_row.get('currency'),
            average_user_rating=appdata_row.get('average_user_rating'),
            average_user_rating_current_version=appdata_row.get('average_user_rating_current_version'),
            user_rating_count=appdata_row.get('user_rating_count'),
            user_rating_current_version=appdata_row.get('user_rating_current_version'),
            developer_id=appdata_row.get('developer_id'),
            developer_name=appdata_row.get('developer_name'),
            developer_view_url=appdata_row.get('developer_view_url'),
            seller_name=appdata_row.get('seller_name'),
            seller_url=appdata_row.get('seller_url'),
            app_content_rating=appdata_row.get('app_content_rating'),
            content_advisory_rating=appdata_row.get('content_advisory_rating'),
            file_size_bytes=appdata_row.get('file_size_bytes'),
            minimum_os_version=appdata_row.get('minimum_os_version'),
            version=appdata_row.get('version'),
            release_date=appdata_row.get('release_date'),
            release_notes=appdata_row.get('release_notes'),
            current_version_release_date=appdata_row.get('current_version_release_date'),
            artwork_url100=appdata_row.get('artwork_url100'),
            app_view_url=appdata_row.get('app_view_url'),
            artwork_url512=appdata_row.get('artwork_url512'),
            artwork_url60=appdata_row.get('artwork_url60'),
            extract_date=appdata_row.get('extract_date'),
            categories=categories,
            ipad_screenshot_urls=ipad_screenshot_urls,
            screenshot_urls=screenshot_urls
        )

        return app_data


    def get(self, id_value: int) -> AppData:
        """Retrieve app data by ID and return an AppData object.

        This method coordinates the retrieval of application data, categories,
        and related URLs using the provided application ID. It fetches the
        raw app data, categories, and URLs, and then constructs an AppData
        object containing all the relevant information.

        Args:
            id_value (int): The unique identifier of the application whose
                            data is to be retrieved.

        Returns:
            AppData: An instance of the AppData class populated with the
                    retrieved application information.

        Raises:
            ValueError: If the application data cannot be found for the
                        given ID.
        """
        appdata_row = self.get_appdata(id_value)
        categories = self.get_categories(id_value)
        urls = self.get_urls(id_value)
        return self.constitute_appdata(appdata_row=appdata_row, categories=categories, urls=urls)


    def get_by_category(self, category: Category) -> pd.DataFrame:
        """
        Retrieves AppData by category ID.

        Note: This method returns a DataFrame, without alternate categories,
        and lists of screenshos.

        Args:
            category (Category): The enum of the category to filter by.

        Returns:
            pd.DataFrame: A DataFrame containing app data for the specified category.
        """
        # Define the raw SQL query to join appdata and category_app tables
        query = """
        SELECT *
        FROM appdata
        WHERE category_id = :category_id
        """

        return self._database.query(query=query, params={"category_id": category.value})


    def batch_upsert_appdata(self, app_data_list: List[AppData]) -> None:
        """
        Batch upsert multiple app data records into the database.

        This method takes a list of AppData objects and performs an
        upsert operation, which inserts new records or updates
        existing ones based on their unique identifiers.
        If the provided list is empty, the method will return
        without making any database operations.

        Args:
            app_data_list (List[AppData]): A list of AppData objects
                                            to be inserted or updated
                                            in the database.

        Returns:
            None: This method does not return a value.

        Raises:
            Exception: May raise exceptions related to database operations,
                    such as connection errors or integrity constraint violations.

        Example:
            app_data_list = [AppData(...), AppData(...)]
            batch_upsert_appdata(app_data_list)
        """
        if not app_data_list:
            return

            # Prepare the upsert SQL statement

        query = """
            INSERT INTO appdata (app_id, app_name, app_censored_name, bundle_id, description,
                                category_id, category, price, currency, average_user_rating,
                                average_user_rating_current_version, user_rating_count,
                                user_rating_current_version, developer_id, developer_name,
                                developer_view_url, seller_name, seller_url,
                                app_content_rating, content_advisory_rating,
                                file_size_bytes, minimum_os_version, version,
                                release_date, release_notes, current_version_release_date,
                                artwork_url100, app_view_url, artwork_url512, artwork_url60,
                                extract_date)
            VALUES (:app_id, :app_name, :app_censored_name, :bundle_id, :description,
                    :category_id, :category, :price, :currency, :average_user_rating,
                    :average_user_rating_current_version, :user_rating_count,
                    :user_rating_current_version, :developer_id, :developer_name,
                    :developer_view_url, :seller_name, :seller_url,
                    :app_content_rating, :content_advisory_rating,
                    :file_size_bytes, :minimum_os_version, :version,
                    :release_date, :release_notes, :current_version_release_date,
                    :artwork_url100, :app_view_url, :artwork_url512, :artwork_url60,
                    :extract_date)
            ON DUPLICATE KEY UPDATE
                app_name = VALUES(app_name),
                app_censored_name = VALUES(app_censored_name),
                bundle_id = VALUES(bundle_id),
                description = VALUES(description),
                category_id = VALUES(category_id),
                category = VALUES(category),
                price = VALUES(price),
                currency = VALUES(currency),
                average_user_rating = VALUES(average_user_rating),
                average_user_rating_current_version = VALUES(average_user_rating_current_version),
                user_rating_count = VALUES(user_rating_count),
                user_rating_current_version = VALUES(user_rating_current_version),
                developer_id = VALUES(developer_id),
                developer_name = VALUES(developer_name),
                developer_view_url = VALUES(developer_view_url),
                seller_name = VALUES(seller_name),
                seller_url = VALUES(seller_url),
                app_content_rating = VALUES(app_content_rating),
                content_advisory_rating = VALUES(content_advisory_rating),
                file_size_bytes = VALUES(file_size_bytes),
                minimum_os_version = VALUES(minimum_os_version),
                version = VALUES(version),
                release_date = VALUES(release_date),
                release_notes = VALUES(release_notes),
                current_version_release_date = VALUES(current_version_release_date),
                artwork_url100 = VALUES(artwork_url100),
                app_view_url = VALUES(app_view_url),
                artwork_url512 = VALUES(artwork_url512),
                artwork_url60 = VALUES(artwork_url60),
                extract_date = VALUES(extract_date)
            """

            # Prepare parameters for batch insert
        param_list = [
                {
                    "app_id": app_data.app_id,
                    "app_name": app_data.app_name,
                    "app_censored_name": app_data.app_censored_name,
                    "bundle_id": app_data.bundle_id,
                    "description": app_data.description,
                    "category_id": app_data.category_id,
                    "category": app_data.category,
                    "price": app_data.price,
                    "currency": app_data.currency,
                    "average_user_rating": app_data.average_user_rating,
                    "average_user_rating_current_version": app_data.average_user_rating_current_version,
                    "user_rating_count": app_data.user_rating_count,
                    "user_rating_current_version": app_data.user_rating_current_version,
                    "developer_id": app_data.developer_id,
                    "developer_name": app_data.developer_name,
                    "developer_view_url": app_data.developer_view_url,
                    "seller_name": app_data.seller_name,
                    "seller_url": app_data.seller_url,
                    "app_content_rating": app_data.app_content_rating,
                    "content_advisory_rating": app_data.content_advisory_rating,
                    "file_size_bytes": app_data.file_size_bytes,
                    "minimum_os_version": app_data.minimum_os_version,
                    "version": app_data.version,
                    "release_date": app_data.release_date,
                    "release_notes": app_data.release_notes,
                    "current_version_release_date": app_data.current_version_release_date,
                    "artwork_url100": app_data.artwork_url100,
                    "app_view_url": app_data.app_view_url,
                    "artwork_url512": app_data.artwork_url512,
                    "artwork_url60": app_data.artwork_url60,
                    "extract_date": app_data.extract_date
                }
                for app_data in app_data_list
            ]

        # Execute the batch upsert query
        self._database.execute_many(query=query, param_list=param_list)

        # Handle categories and URLs for all app_data
        for app_data in app_data_list:
            self.upsert_categories(app_data.app_id, app_data.categories)
            self.upsert_urls(app_data.app_id, app_data.ipad_screenshot_urls, AppDataURLType.IPAD)
            self.upsert_urls(app_data.app_id, app_data.screenshot_urls, AppDataURLType.SCREENSHOT)


    def upsert_categories(self, app_id: int, categories: List[int]) -> None:
        """
        Upsert categories associated with the specified app.

        This method takes an app ID and a list of category IDs,
        and performs an upsert operation to associate the
        provided categories with the app. If the categories list
        is empty, the method will return without making any changes.

        Args:
            app_id (int): The unique identifier of the app for which
                        categories are being upserted.
            categories (List[int]): A list of category IDs to be
                                    associated with the app.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: If the app_id is invalid or if there are
                        issues with the database operation.

        Example:
            app_id = 12345
            categories = [1, 2, 3]
            upsert_categories(app_id, categories)
        """
        if not categories:
            return


        # First delete existing categories for the app
        query = """
        DELETE FROM category_app WHERE app_id = :app_id
        """

        params={"app_id": app_id}
        with self._database as db:
            db.execute(query=query, params=params)

        # Insert new categories for the app
        query = """
        INSERT INTO category_app (app_id, category_id) VALUES (:app_id, :category_id)
        """
        for category_id in categories:
            params = {"app_id": app_id, "category_id": category_id}
            with self._database as db:
                db.execute(query=query, params=params)

    def upsert_urls(self, app_id: int, urls: List[str], url_type: AppDataURLType) -> None:
        """
        Upsert URLs associated with the specified app.

        This method takes an app ID, a list of URLs, and a URL type,
        and performs an upsert operation to associate the provided
        URLs with the app. If the URLs list is empty, the method
        will return without making any changes.

        Args:
            app_id (int): The unique identifier of the app for which
                        URLs are being upserted.
            urls (List[str]): A list of URLs to be associated with
                            the app.
            url_type (AppDataURLType): The type of the URLs being
                                        associated (e.g., screenshot,
                                        iPad).

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: If the app_id is invalid or if there are
                        issues with the database operation.

        Example:
            app_id = 12345
            urls = ['http://example.com/image1.png', 'http://example.com/image2.png']
            url_type = AppDataURLType.SCREENSHOT
            upsert_urls(app_id, urls, url_type)
        """
        if not urls:
            return


        # First delete existing URLs for the app of a specific type
        query = """
        DELETE FROM app_url WHERE app_id = :app_id AND url_type = :url_type
        """
        params={"app_id": app_id, "url_type": url_type.value}
        with self._database as db:
            db.execute(query=query, params=params)

        # Insert new URLs for the app
        query = """
        INSERT INTO app_url (app_id, url_type, url) VALUES (:app_id, :url_type, :url)
        """
        for url in urls:
            params = {"app_id": app_id, "url_type": url_type.value, "url": url}
            with self._database as db:
                db.execute(query=query, params=params)
