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
# Modified   : Saturday August 31st 2024 02:23:02 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import logging
from typing import Any, Dict, List

import pandas as pd

from appvocai.core.enum import Category
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

    def _init_(self, database: MySQLDatabase) -> None:
        """Initializes the AppDataRepo with a given database instance.

        Args:
            database (MySQLDatabase): The database connection instance.
        """

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

    def get_app_categories(self, id_value: int) -> List[int]:
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
        categories = self.get_app_categories(id_value)
        return self._constitute_appdata(appdata_row=appdata_row, categories=categories)


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


    def add(self, app_data_list: List[AppData]) -> None:
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
                                category_id, category, price, currency, rating_average,
                                rating_average_current_version, rating_average_current_version_change,
                                rating_average_current_version_pct_change, rating_count,
                                rating_count_current_version, developer_id, developer_name,
                                seller_name,  app_content_rating, content_advisory_rating,
                                file_size_bytes, minimum_os_version, version,
                                release_date, release_notes, release_date_current_version,
                                url_developer_view, url_seller, url_app_view, url_artwork_100,
                                url_artwork_512, url_artwork_60, extract_date)
            VALUES (:app_id, :app_name, :app_censored_name, :bundle_id, :description,
                    :category_id, :category, :price, :currency, :rating_average,
                    :rating_average_current_version, :rating_count,
                    :rating_count_current_version, :developer_id, :developer_name,
                    :seller_name, :app_content_rating, :content_advisory_rating,
                    :file_size_bytes, :minimum_os_version, :version,
                    :release_date, :release_notes, :release_date_current_version,
                    :url_developer_view, :url_seller, :url_app_view,
                    :url_artwork_100, :url_artwork_512, :url_artwork_60,
                    :urls_screenshot_ipad, :urls_screenshot_iphone,
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
                rating_average = VALUES(rating_average),
                rating_average_current_version = VALUES(rating_average_current_version),
                rating_average_current_version_change = VALUES(rating_average_current_version_change),
                rating_average_current_version_pct_change = VALUES(rating_average_current_version_pct_change),
                rating_count = VALUES(rating_count),
                rating_count_current_version = VALUES(rating_count_current_version),
                developer_id = VALUES(developer_id),
                developer_name = VALUES(developer_name),
                seller_name = VALUES(seller_name),
                app_content_rating = VALUES(app_content_rating),
                content_advisory_rating = VALUES(content_advisory_rating),
                file_size_bytes = VALUES(file_size_bytes),
                minimum_os_version = VALUES(minimum_os_version),
                version = VALUES(version),
                release_date = VALUES(release_date),
                release_notes = VALUES(release_notes),
                release_date_current_version = VALUES(release_date_current_version),
                url_developer_view = VALUES(url_developer_view),
                url_seller = VALUES(url_seller),
                url_app_view = VALUES(url_app_view),
                url_artwork_100 = VALUES(url_artwork_100),
                url_artwork_512 = VALUES(url_artwork_512),
                url_artwork_60 = VALUES(url_artwork_60),
                urls_screenshot_ipad = VALUES(urls_screenshot_ipad),
                urls_screenshot_iphone = VALUES(urls_screenshot_iphone),
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
                    "rating_average": app_data.rating_average,
                    "rating_average_current_version": app_data.rating_average_current_version,
                    "rating_average_current_version_change": app_data.rating_average_current_version_change,
                    "rating_average_current_version_pct_change": app_data.rating_average_current_version_pct_change,
                    "rating_count": app_data.rating_count,
                    "rating_count_current_version": app_data.rating_count_current_version,
                    "developer_id": app_data.developer_id,
                    "developer_name": app_data.developer_name,
                    "seller_name": app_data.seller_name,
                    "app_content_rating": app_data.app_content_rating,
                    "content_advisory_rating": app_data.content_advisory_rating,
                    "file_size_bytes": app_data.file_size_bytes,
                    "minimum_os_version": app_data.minimum_os_version,
                    "version": app_data.version,
                    "release_date": app_data.release_date,
                    "release_notes": app_data.release_notes,
                    "release_date_current_version": app_data.release_date_current_version,
                    "url_developer_view": app_data.url_developer_view,
                    "url_seller": app_data.url_seller,
                    "url_app_view": app_data.url_app_view,
                    "url_artwork_100": app_data.url_artwork_100,
                    "url_artwork_512": app_data.url_artwork_512,
                    "url_artwork_60": app_data.url_artwork_60,
                    "urls_screenshot_ipad": app_data.urls_screenshot_ipad,
                    "urls_screenshot_iphone": app_data.urls_screenshot_iphone,
                    "extract_date": app_data.extract_date
                }
                for app_data in app_data_list
            ]

        # Execute the batch upsert query
        self._database.execute_many(query=query, param_list=param_list)

        # Handle categories and URLs for all app_data
        for app_data in app_data_list:
            if app_data.categories:
                self._add_app_categories(app_data.app_id, app_data.categories)


    def _add_app_categories(self, app_id: int, categories: List[int]) -> None:
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
            add_app_categories(app_id, categories)
        """
        if not categories:
            return


        # First delete existing categories for the app
        query = """
        DELETE FROM category_app WHERE app_id = :app_id;
        """

        params={"app_id": app_id}
        with self._database as db:
            db.execute(query=query, params=params)

        # Insert new categories for the app
        query = """
        INSERT INTO category_app (app_id, category_id) VALUES (:app_id, :category_id);
        """
        for category_id in categories:
            params = {"app_id": app_id, "category_id": category_id}
            with self._database as db:
                db.execute(query=query, params=params)

    def remove(self, id_value: int) -> None:
        self._remove_app_data(id_value=id_value)
        self._remove_category_app_data(id_value=id_value)

    def _remove_app_data(self, id_value: int) -> None:
        """
        Deletes an entry from the appdata table based on the provided app_id.

        Args:
            app_id (int): The ID of the app to delete from the appdata table.

        Raises:
            Exception: If the delete operation fails due to a database error.
        """
        query = "DELETE FROM appdata WHERE app_id = :app_id"
        params = {"app_id": id_value}

        try:
            self._database.execute(query, params)
        except Exception as e:
            # Handle exceptions or log them as necessary
            raise Exception(f"Failed to delete app with ID {id_value}: {str(e)}")

    def _remove_category_app_data(self, id_value: int) -> None:
        """
        Deletes an entry from the appdata table based on the provided app_id.

        Args:
            app_id (int): The ID of the app to delete from the appdata table.

        Raises:
            Exception: If the delete operation fails due to a database error.
        """
        query = "DELETE FROM category_app WHERE app_id = :app_id"
        params = {"app_id": id_value}

        try:
            self._database.execute(query, params)
        except Exception as e:
            # Handle exceptions or log them as necessary
            raise Exception(f"Failed to delete category_app data with ID {id_value}: {str(e)}")

    def remove_by_category_id(self, category_id: int) -> None:
        self._remove_appdata_by_category_id(category_id=category_id)
        self._remove_appdata_categories_by_category_id(category_id=category_id)


    def _remove_appdata_by_category_id(self, category_id: int) -> None:
        """
        Deletes entries from the appdata table based on the provided category_id.

        Args:
            category_id (int): The ID of the category to delete from the appdata table.

        Raises:
            Exception: If the delete operation fails due to a database error.
        """
        query = "DELETE FROM appdata WHERE category_id = :category_id;"
        params = {"category_id": category_id}

        try:
            self._database.execute(query, params)
        except Exception as e:
            # Handle exceptions or log them as necessary
            raise Exception(f"Failed to delete entries with category ID {category_id}: {str(e)}")


    def _remove_appdata_categories_by_category_id(self, category_id: int) -> None:
        """
        Deletes entries from the appdata table based on the provided category_id.

        Args:
            category_id (int): The ID of the category to delete from the appdata table.

        Raises:
            Exception: If the delete operation fails due to a database error.
        """
        query = "DELETE FROM category_app WHERE category_id = :category_id;"
        params = {"category_id": category_id}

        try:
            self._database.execute(query, params)
        except Exception as e:
            # Handle exceptions or log them as necessary
            raise Exception(f"Failed to delete entries with category ID {category_id}: {str(e)}")

    def remove_all(self) -> None:
        """
        Prompts the user for confirmation before deleting all entries from the appdata tables.

        The method asks the user to confirm the deletion of all entries from the appdata tables.
        If the user confirms by typing 'yes', the deletion is carried out; otherwise, the operation is canceled.

        Returns:
            None
        """
        confirmation = input("Are you sure you want to delete all entries from the appdata tables? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Deletion canceled.")
            return
        else:
            self._remove_all_appdata()


    def _remove_all_appdata(self) -> None:
        """
        Deletes all entries from the appdata table after user confirmation.

        This method performs the actual deletion of all records from the appdata table in the database.
        It should be called only after user confirmation through the `remove_all` method.

        Raises:
            Exception: If the delete operation fails due to a database error.

        Returns:
            None
        """

        query = "DELETE FROM appdata;"
        try:
            self._database.execute(query)
            print("All entries from the appdata table have been deleted.")
        except Exception as e:
            # Handle exceptions or log them as necessary
            raise Exception(f"Failed to delete all entries from appdata: {str(e)}")

    def _remove_all_category_app_data(self) -> None:
        """
        Deletes all entries from the category_app table.

        This method deletes all records from the category_app table in the database.
        It is meant to be used for operations where all category-specific app data needs to be purged.

        Raises:
            Exception: If the delete operation fails due to a database error.

        Returns:
            None
        """
        query = "DELETE FROM category_app;"
        try:
            self._database.execute(query)
            print("All entries from the appdata table have been deleted.")
        except Exception as e:
            # Handle exceptions or log them as necessary
            raise Exception(f"Failed to delete all entries from appdata: {str(e)}")

    def _constitute_appdata(
        self, appdata_row: Dict[str, Any], categories: List[int]) -> AppData:
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
            self._logger.exception(msg)
            raise ValueError(msg)

        # Use default values for optional fields
        app_name = appdata_row.get('app_name', "Unknown")
        app_censored_name = appdata_row.get('app_censored_name', "Unknown")
        bundle_id = appdata_row.get('bundle_id', "Unknown")


        # Log the successful creation of an AppData object
        app_data = AppData(
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

        return app_data
