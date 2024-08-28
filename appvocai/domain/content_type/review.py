#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/entity/review.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 12:59:37 am                                              #
# Modified   : Wednesday August 28th 2024 01:03:28 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass
from datetime import datetime

from appvocai.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppReview(DataClass):
    """
    A dataclass representing a review for an app from the App Store.

    Attributes:
        review_id (str): The unique identifier for the review.
        review (str): The text of the review.
        review_date (datetime): The date and time the review was posted.
        reviewer_name (str): The name of the reviewer.
        rating (int): The rating given by the reviewer (usually out of 5).
        review_title (str): The title of the review.
        vote_count (int): The number of votes the review received.
        vote_sum (int): The sum of votes (typically, upvotes - downvotes).
        is_edited (bool): Indicates whether the review was edited.
        reviews_url (str): The URL to the review page.
        vote_url (str): The URL to the vote page.
        customer_type (str): The type of customer (e.g., verified, anonymous).
    """

    review_id: str
    review: str
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

