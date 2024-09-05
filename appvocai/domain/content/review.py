#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/content/review.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 12:59:37 am                                              #
# Modified   : Wednesday September 4th 2024 08:42:08 pm                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from appvocai.domain.content.base import Entity

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppReview(Entity):
    """
    A dataclass representing a review for an application.

    Attributes:
        review_id (str): The unique identifier for the review.
        app_id (int): The unique identifier for the app.
        review (str): The text content of the review.
        review_length (int): Review length in words.
        review_date (datetime): The date when the review was posted.
        reviewer_name (str): The name of the reviewer.
        rating (int): The rating given by the reviewer.
        review_title (str): The title of the review.
        vote_count (int): The number of votes the review received.
        vote_sum (int): The sum of the votes.
        is_edited (bool): Whether the review has been edited.
        reviews_url (str): The URL to the review on the App Store.
        vote_url (str): The URL to vote for the review.
        customer_type (str): The type of customer (e.g., regular, verified).
        extract_date (datetime): Date the review was extracted.
    """

    review_id: str
    app_id: int
    review: str
    review_length: int
    review_date: datetime
    reviewer_name: str
    rating: int
    review_title: str
    vote_count: int
    vote_sum: int
    is_edited: bool
    reviews_url: str
    vote_url: str
    customer_type: str
    extract_date: datetime

    @classmethod
    def create(cls, appreview_row: Dict[str, Any]) -> AppReview:
        """
        Create an AppReview object from the retrieved review data.

        Args:
            appreview_row (Dict[str, Any]): A dictionary containing review data fields.

        Returns:
            AppReview: An instance of the AppReview class populated with the provided data.

        Raises:
            ValueError: If review_id, app_id, or any other required field is missing.

        Logs:
            - Logs an error if review_id or app_id is None.
            - Logs the successful creation of an AppReview object.
        """
        # Extract and validate mandatory fields
        review_id = appreview_row.get("review_id")
        app_id = appreview_row.get("app_id")

        # Ensure that the critical fields are present
        if not review_id or not app_id:
            msg = "review_id and app_id cannot be None"
            logger.exception(msg)
            raise ValueError(msg)

        # Create and return the AppReview object
        return cls(
            review_id=review_id,
            app_id=app_id,
            review=appreview_row.get("review", "No review text provided"),
            review_length=appreview_row.get("review_length", 0),
            review_date=appreview_row.get("review_date", datetime.min),
            reviewer_name=appreview_row.get("reviewer_name", "Anonymous"),
            rating=appreview_row.get("rating", 0),
            review_title=appreview_row.get("review_title", "No title"),
            vote_count=appreview_row.get("vote_count", 0),
            vote_sum=appreview_row.get("vote_sum", 0),
            is_edited=appreview_row.get("is_edited", False),
            reviews_url=appreview_row.get("reviews_url", ""),
            vote_url=appreview_row.get("vote_url", ""),
            customer_type=appreview_row.get("customer_type", "Unknown"),
            extract_date=appreview_row.get("extract_date", datetime.min),
        )
