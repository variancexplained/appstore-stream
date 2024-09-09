#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/repo/content/review.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 10:27:12 pm                                                 #
# Modified   : Saturday September 7th 2024 11:10:49 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Review Repo Module"""
import logging
from typing import Any, Dict, cast

import pandas as pd

from appvocai.core.enum import Category
from appvocai.domain.content.review import AppReview
from appvocai.domain.repo.base import Repo
from appvocai.infra.database.mysql import MySQLDatabase
from appvocai.infra.exceptions.database import DatabaseError


# ------------------------------------------------------------------------------------------------ #
class ReviewRepo(Repo):
    """Repository class for handling stages on the 'review' table.

    Args:
        database (MySQLDatabase): The database instance used for stages.
    """

    __table_name = "review"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the ReviewRepo with a database connection.

        """
        self._database = database
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get(self, id_value: int) -> AppReview:
        """
        Fetches data from the 'review' table based on the app_id.

        Args:
            category_id (int): The ID of the category to fetch data for.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """
        # Construct SQL query using the category_id
        query = """
        SELECT * FROM review
        WHERE app_id = :app_id
        """
        params = {"app_id": id_value}

        # Use the database connection to execute the query and return the result as a DataFrame
        try:
            with self._database as db:
                result = db.execute(query=query, params=params)
            appreview_row = result.fetchone()
            appreview_dict = dict(appreview_row) if appreview_row else {}
            return AppReview.create(appreview_row=appreview_dict)
        except Exception as e:
            # Log the exception and raise a custom DatabaseError
            self._logger.exception(
                f"Failed to delete reviews for app_id '{id_value}': {e}"
            )
            raise DatabaseError(
                f"An error occurred while deleting reviews for app_id '{id_value}'"
            ) from e

    def get_by_category_id(self, category: Category) -> pd.DataFrame:
        """
        Retrieves reviews from the 'review' table filtered by the specified category ID.

        This method constructs an SQL query to select all records from the 'review' table where
        the `category_id` matches the value provided by the `Category` enum. The results of the
        query are returned as a Pandas DataFrame.

        Args:
            category (Category): An instance of the `Category` enum representing the category ID
                                to filter the reviews by.

        Returns:
            pd.DataFrame: A DataFrame containing the reviews that match the specified category ID.

        Example:
            df = repository.get_by_category_id(Category.GAMES)
            # df will contain all reviews associated with the 'GAMES' category.
        """
        # Construct SQL query using the category_id
        query = """
        SELECT * FROM review
        WHERE category_id = :category_id
        """
        params = {"category_id": category.value}

        # Use the database connection to execute the query and return the result as a DataFrame
        try:
            with self._database as db:
                return db.query(query=query, params=params)
        except Exception as e:
            # Log the exception and raise a custom DatabaseError
            self._logger.exception(
                f"Failed to read reviews for category '{category.name}': {e}"
            )
            raise DatabaseError(
                f"An error occurred while reading reviews for category '{category.name}'"
            ) from e

    def add(self, data: pd.DataFrame) -> int:
        """
        Upserts (inserts or updates) data into the 'review' table.

        Args:
            data (pd.DataFrame): DataFrame containing the data to upsert.

        Returns:
            int: Number of rows affected by the upsert stage.
        """
        # Convert DataFrame to a list of dictionaries for the upsert stage
        data_dict = data.to_dict(orient="records")

        # Construct the upsert SQL query
        query = """
            INSERT INTO review (
                review_id,
                app_id,
                review,
                review_length,
                review_date,
                reviewer_name,
                rating,
                review_title,
                vote_count,
                vote_sum,
                is_edited,
                reviews_url,
                vote_url,
                customer_type,
                extract_date
            ) VALUES (
                :review_id,
                :app_id,
                :review,
                :review_length,
                :review_date,
                :reviewer_name,
                :rating,
                :review_title,
                :vote_count,
                :vote_sum,
                :is_edited,
                :reviews_url,
                :vote_url,
                :customer_type,
                :extract_date
            ) ON DUPLICATE KEY UPDATE
                app_id = VALUES(app_id),
                review = VALUES(review),
                review_length = VALUES(review_length),
                review_date = VALUES(review_date),
                reviewer_name = VALUES(reviewer_name),
                rating = VALUES(rating),
                review_title = VALUES(review_title),
                vote_count = VALUES(vote_count),
                vote_sum = VALUES(vote_sum),
                is_edited = VALUES(is_edited),
                reviews_url = VALUES(reviews_url),
                vote_url = VALUES(vote_url),
                customer_type = VALUES(customer_type),
                extract_date = VALUES(extract_date);
            """

        # Execute the upsert query for each record
        try:
            with self._database as db:
                upsert_count = 0
                for record in data_dict:
                    params = cast(Dict[str, Any], record)
                    result = db.execute(query=query, params=params)
                    upsert_count += (
                        result.rowcount if hasattr(result, "rowcount") else 0
                    )
                return upsert_count

        except Exception as e:
            # Log the exception and raise a custom DatabaseError
            msg = f"Failed to execute upsert of reviews.\n{e}"
            self._logger.exception(msg)
            raise DatabaseError(f"An error occurred while upserting reviews.") from e

    def remove(self, id_value: int) -> int:
        """
        Removes reviews from the 'review' table based on the specified app_id.

        This method constructs an SQL query to delete all records from the 'review' table where
        the `app_id` matches the provided `id_value`. The method returns the number of rows
        affected by the deletion.

        Args:
            id_value (int): The `app_id` value to filter the reviews by.

        Returns:
            int: The number of rows affected by the delete stage.

        Example:
            deleted_count = repository.remove(123456)
            # deleted_count will contain the number of reviews removed with app_id 123456.
        """
        # Construct SQL query to delete records with the specified app_id
        query = """
        DELETE FROM review
        WHERE app_id = :app_id
        """
        params = {"app_id": id_value}

        # Use the database connection to execute the delete query
        try:
            with self._database as db:
                count = 0

                result = db.execute(query=query, params=params)
                if hasattr(result, "rowcount"):
                    if isinstance(result.rowcount, int):
                        count = result.rowcount
                return count
        except Exception as e:
            # Log the exception and raise a custom DatabaseError
            self._logger.exception(
                f"Failed to delete reviews for app_id '{id_value}': {e}"
            )
            raise DatabaseError(
                f"An error occurred while deleting reviews for app_id '{id_value}'"
            ) from e

    def remove_by_category(self, category: Category) -> int:
        """
        Removes reviews from the 'review' table based on the specified category ID.

        This method constructs an SQL query to delete all records from the 'review' table where
        the `category_id` matches the value provided by the `Category` enum. The method returns
        the number of rows affected by the deletion.

        Args:
            category (Category): An instance of the `Category` enum representing the category ID
                                to filter the reviews by.

        Returns:
            int: The number of rows affected by the delete stage.

        Raises:
            DatabaseError: If an error occurs during the database stage.

        Example:
            deleted_count = repository.remove_by_category(Category.GAMES)
            # deleted_count will contain the number of reviews removed with the 'GAMES' category ID.
        """

        # Construct SQL query to delete records with the specified category_id
        query = """
        DELETE FROM review
        WHERE category_id = :category_id
        """
        params = {"category_id": category.value}

        # Use the database connection to execute the delete query
        try:
            with self._database as db:
                result = db.execute(query=query, params=params)
                if hasattr(result, "rowcount"):
                    if isinstance(result.rowcount, int):
                        count = result.rowcount
                        self._logger.info(
                            f"Removed {count} rows from the reviews table."
                        )
                return count

        except Exception as e:
            # Log the exception and raise a custom DatabaseError
            self._logger.exception(
                f"Failed to delete reviews for category '{category.name}': {e}"
            )
            raise DatabaseError(
                f"An error occurred while deleting reviews for category '{category.name}'"
            ) from e

    def remove_all(self) -> int:
        """
        Removes all reviews from the 'review' table after user confirmation.

        This method prompts the user for confirmation before deleting all records from the 'review' table.
        If the user confirms, it will delete all reviews and return the number of rows affected.

        Returns:
            int: The number of rows affected by the delete stage.

        Raises:
            DatabaseError: If an error occurs during the database stage.

        Example:
            deleted_count = repository.remove_all_reviews()
            # deleted_count will contain the number of reviews removed.
        """
        # Ask for user confirmation
        confirmation = input(
            "Are you sure you want to delete all reviews? This action cannot be undone. (yes/no): "
        )

        if confirmation.lower() != "yes":
            print("Stage cancelled.")
            return 0

        try:
            # Construct SQL query to delete all records in the review table
            query = "DELETE FROM review"

            # Execute the delete query
            with self._database as db:
                result = db.execute(query=query)
                if hasattr(result, "rowcount"):
                    if isinstance(result.rowcount, int):
                        count = result.rowcount
                        self._logger.info(
                            f"Removed {count} rows from the reviews table."
                        )
                return count

        except Exception as e:
            # Log the exception and raise a custom DatabaseError
            self._logger.exception("Failed to delete all reviews: {e}")
            raise DatabaseError("An error occurred while deleting all reviews") from e
