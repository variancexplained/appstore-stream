#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/repo/appdata.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 10:27:12 pm                                                 #
# Modified   : Sunday August 25th 2024 12:11:46 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import pandas as pd
from sqlalchemy.types import BIGINT, DATETIME, DECIMAL, INTEGER, JSON, TEXT, VARCHAR

from appstorestream.domain.base.repo import DomainLayerRepo
from appstorestream.infra.database.mysql import MySQLDatabase

# ------------------------------------------------------------------------------------------------ #
DTYPE = {
    "app_id": BIGINT,
    "app_name": VARCHAR,
    "app_description": TEXT,
    "category_id": INTEGER,
    "category": VARCHAR,
    "developer_id": BIGINT,
    "developer": VARCHAR,
    "developer_url": VARCHAR,
    "seller_name": VARCHAR,
    "seller_url": VARCHAR,
    "price": DECIMAL,
    "rating_average": DECIMAL,
    "rating_average_current_version": DECIMAL,
    "rating_average_current_version_change": DECIMAL,
    "rating_average_current_version_pct_change": DECIMAL,
    "rating_count": BIGINT,
    "rating_count_current_version": BIGINT,
    "rating_count_per_day": DECIMAL,
    "rating_count_per_day_current_version": DECIMAL,
    "rating_count_per_day_current_version_pct_change": DECIMAL,
    "app_url": VARCHAR,
    "screenshot_urls": JSON,
    "release_date": DATETIME,
    "release_date_current_version": DATETIME,
    "app_version": VARCHAR,
    "software_lifecycle_response_time": INTEGER,
    "days_since_release": INTEGER,
    "days_since_current_version": INTEGER,
    "extract_date": DATETIME,
}


# ------------------------------------------------------------------------------------------------ #
class AppDataRepo(DomainLayerRepo):
    """Repository class for handling operations on the 'appdata' table.

    Args:
        database (MySQLDatabase): The database instance used for operations.
    """

    __tablename = "appdata"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the AppDataRepo with a database connection.

        """
        super().__init__()
        self._database = database

    def get(self, category_id: int) -> pd.DataFrame:
        """
        Fetches data from the 'appdata' table based on the category_id.

        Args:
            category_id (int): The ID of the category to fetch data for.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """
        # Construct SQL query using the category_id
        query = """
        SELECT * FROM appdata
        WHERE category_id = :category_id
        """
        params = {"category_id": category_id}

        # Use the database connection to execute the query and return the result as a DataFrame
        with self._database as conn:
            return conn.query(query, params)

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
