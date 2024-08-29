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
# Modified   : Thursday August 29th 2024 05:14:17 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from typing import Any, Dict, List

import pandas as pd

from appvocai.core.enum import AppDataURLType, Category
from appvocai.domain.content.appdata import AppData
from appvocai.domain.repo.base import Repo
from appvocai.infra.database.mysql import MySQLDatabase


# ------------------------------------------------------------------------------------------------ #
class AppDataRepo(Repo):
    """Repository class for handling operations on the 'appdata' table.

    Args:
        database (MySQLDatabase): The database instance used for operations.
    """

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the AppDataRepo with a database connection.

        """
        super().__init__()
        self._database = database

    def get_appdata(self, id_value: int) -> Dict[str, Any]:
        """
        Retrieve a single app's data from the appdata table.
        """
        query = """
        SELECT * FROM appdata
        WHERE app_id = :app_id
        """
        params = {"app_id": id_value}

        # Use the database connection to execute the query and return the result
        with self._database as conn:
            return conn.query(query, params)

    def get_categories(self, id_value: int) -> List[int]:
        """
        Retrieve the categories associated with a specific app.
        """
        query = """
        SELECT category_id FROM category_app
        WHERE app_id = :app_id
        """
        params = {"app_id": id_value}

        with self._database as conn:
            rows = conn.query(query, params)
            return [row['category_id'] for row in rows]

    def get_urls(self, id_value: int) -> List[Dict[str, str]]:
        """
        Retrieve URLs associated with a specific app.
        """
        query = """
        SELECT url_type, url FROM app_url
        WHERE app_id = :app_id
        """
        params = {"app_id": id_value}

        with self._database as conn:
            return conn.query(query, params)

    def constitute_appdata(self, appdata_row: Dict[str, Any], categories: List[int], urls: List[Dict[str, str]]) -> AppData:
        """
        Create an AppData object from the retrieved data.
        """
        ipad_screenshot_urls = [url['url'] for url in urls if url['url_type'] == AppDataURLType.IPAD.value]
        screenshot_urls = [url['url'] for url in urls if url['url_type'] == AppDataURLType.SCREENSHOT.value]

        return AppData(
            app_id=appdata_row['app_id'],
            app_name=appdata_row['app_name'],
            app_censored_name=appdata_row['app_censored_name'],
            bundle_id=appdata_row['bundle_id'],
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

    def get(self, id_value: int) -> AppData:
        """
        Coordinate retrieval of app data and return an AppData object.
        """
        appdata_row = self.get_appdata(id_value)
        categories = self.get_categories(id_value)
        urls = self.get_urls(id_value)

        return self.constitute_appdata(appdata_row, categories, urls)





    def get_by_category(self, category: Category) -> pd.DataFrame:
        """
        Retrieves AppData by category ID.

        Args:
            category (Category): The enum of the category to filter by.

        Returns:
            pd.DataFrame: A DataFrame containing app data for the specified category.
        """
        # Define the raw SQL query to join appdata and category_app tables
        query = """
        SELECT ad.*
        FROM appdata AS ad
        JOIN category_app AS ca ON ad.app_id = ca.app_id
        WHERE ca.category_id = :category_id
        """

        # Execute the query and fetch results into a DataFrame
        df = pd.read_sql_query(query, self.connection, params={"category_id": category.value})

        return df

    def upsert(self, data: pd.DataFrame) -> int:
        """
        Upserts (inserts or updates) data into the 'appdata' table.

        Args:
            data (pd.DataFrame): DataFrame containing the data to upsert.

        Returns:
            int: Number of rows affected by the upsert operation.
        """
        # Convert DataFrame to a list of dictionaries for upsert operation
        data_dict = data.to_dict(orient="records")

        # Construct the upsert SQL query
        upsert_query = """
        INSERT INTO appdata (
            app_id,
            app_name,
            app_description,
            category_id,
            category,
            developer_id,
            developer,
            developer_url,
            seller_name,
            seller_url,
            price,
            rating_average,
            rating_average_current_version,
            rating_average_current_version_change,
            rating_average_current_version_pct_change,
            rating_count,
            rating_count_current_version,
            rating_count_per_day,
            rating_count_per_day_current_version,
            rating_count_per_day_current_version_pct_change,
            app_url,
            screenshot_urls,
            release_date,
            release_date_current_version,
            app_version,
            software_lifecycle_response_time,
            days_since_release,
            days_since_current_version,
            extract_date
        ) VALUES (
            :app_id,
            :app_name,
            :app_description,
            :category_id,
            :category,
            :developer_id,
            :developer,
            :developer_url,
            :seller_name,
            :seller_url,
            :price,
            :rating_average,
            :rating_average_current_version,
            :rating_average_current_version_change,
            :rating_average_current_version_pct_change,
            :rating_count,
            :rating_count_current_version,
            :rating_count_per_day,
            :rating_count_per_day_current_version,
            :rating_count_per_day_current_version_pct_change,
            :app_url,
            :screenshot_urls,
            :release_date,
            :release_date_current_version,
            :app_version,
            :software_lifecycle_response_time,
            :days_since_release,
            :days_since_current_version,
            :extract_date
        ) ON DUPLICATE KEY UPDATE
            app_name = VALUES(app_name),
            app_description = VALUES(app_description),
            category_id = VALUES(category_id),
            category = VALUES(category),
            developer_id = VALUES(developer_id),
            developer = VALUES(developer),
            developer_url = VALUES(developer_url),
            seller_name = VALUES(seller_name),
            seller_url = VALUES(seller_url),
            price = VALUES(price),
            rating_average = VALUES(rating_average),
            rating_average_current_version = VALUES(rating_average_current_version),
            rating_average_current_version_change = VALUES(rating_average_current_version_change),
            rating_average_current_version_pct_change = VALUES(rating_average_current_version_pct_change),
            rating_count = VALUES(rating_count),
            rating_count_current_version = VALUES(rating_count_current_version),
            rating_count_per_day = VALUES(rating_count_per_day),
            rating_count_per_day_current_version = VALUES(rating_count_per_day_current_version),
            rating_count_per_day_current_version_pct_change = VALUES(rating_count_per_day_current_version_pct_change),
            app_url = VALUES(app_url),
            screenshot_urls = VALUES(screenshot_urls),
            release_date = VALUES(release_date),
            release_date_current_version = VALUES(release_date_current_version),
            app_version = VALUES(app_version),
            software_lifecycle_response_time = VALUES(software_lifecycle_response_time),
            days_since_release = VALUES(days_since_release),
            days_since_current_version = VALUES(days_since_current_version),
            extract_date = VALUES(extract_date);
        """
        # Execute the upsert query for each record
        with self._database as conn:
            upsert_count = 0
            for record in data_dict:
                result = conn.execute(upsert_query, record)
                upsert_count += result.rowcount
            return upsert_count
