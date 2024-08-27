#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/repo/review.py                                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 10:27:12 pm                                                 #
# Modified   : Tuesday August 27th 2024 06:26:13 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Review Repo Module"""
import pandas as pd

from appvocai.domain.base.repo import DomainLayerRepo
from appvocai.infra.database.mysql import MySQLDatabase


# ------------------------------------------------------------------------------------------------ #
class ReviewRepo(DomainLayerRepo):
    """Repository class for handling operations on the 'review' table.

    Args:
        database (MySQLDatabase): The database instance used for operations.
    """

    __tablename = "review"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the ReviewRepo with a database connection.

        """
        super().__init__()
        self._database = database

    def get(self, category_id: int) -> pd.DataFrame:
        """
        Fetches data from the 'review' table based on the category_id.

        Args:
            category_id (int): The ID of the category to fetch data for.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """
        # Construct SQL query using the category_id
        query = """
        SELECT * FROM review
        WHERE category_id = :category_id
        """
        params = {"category_id": category_id}

        # Use the database connection to execute the query and return the result as a DataFrame
        with self._database as conn:
            return conn.query(query, params)

    def upsert(self, data: pd.DataFrame) -> int:
        """
        Upserts (inserts or updates) data into the 'review' table.

        Args:
            data (pd.DataFrame): DataFrame containing the data to upsert.

        Returns:
            int: Number of rows affected by the upsert operation.
        """
        # Convert DataFrame to a list of dictionaries for upsert operation
        data_dict = data.to_dict(orient="records")

        # Construct the upsert SQL query
        upsert_query = """
            INSERT INTO review (
                review_id,
                reviewer_id,
                app_id,
                app_name,
                category_id,
                category,
                title,
                content,
                review_length,
                rating,
                vote_count,
                vote_count_per_day,
                vote_sum,
                vote_sum_per_day,
                vote_avg,
                review_age,
                review_date,
                extract_date
            ) VALUES (
                :review_id,
                :reviewer_id,
                :app_id,
                :app_name,
                :category_id,
                :category,
                :title,
                :content,
                :review_length,
                :rating,
                :vote_count,
                :vote_count_per_day,
                :vote_sum,
                :vote_sum_per_day,
                :vote_avg,
                :review_age,
                :review_date,
                :extract_date
            ) ON DUPLICATE KEY UPDATE
                reviewer_id = VALUES(reviewer_id),
                app_id = VALUES(app_id),
                app_name = VALUES(app_name),
                category_id = VALUES(category_id),
                category = VALUES(category),
                title = VALUES(title),
                content = VALUES(content),
                review_length = VALUES(review_length),
                rating = VALUES(rating),
                vote_count = VALUES(vote_count),
                vote_count_per_day = VALUES(vote_count_per_day),
                vote_sum = VALUES(vote_sum),
                vote_sum_per_day = VALUES(vote_sum_per_day),
                vote_avg = VALUES(vote_avg),
                review_age = VALUES(review_age),
                review_date = VALUES(review_date),
                extract_date = VALUES(extract_date);
            """

        # Execute the upsert query for each record
        with self._database as conn:
            upsert_count = 0
            for record in data_dict:
                result = conn.execute(upsert_query, record)
                upsert_count += result.rowcount
            return upsert_count
