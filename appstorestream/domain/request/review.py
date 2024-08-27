#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/request/review.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 12:26:33 am                                                #
# Modified   : Tuesday August 27th 2024 01:36:49 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass, field
from typing import Any, Collection, Dict

from appstorestream.domain.request.base import Request
from appstorestream.infra.web.header import STOREFRONT


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestReview(Request):
    """Represents a request for AppData.

    Attributes:
        baseurl (str): The base URL for the request.
        param_list (list[Dict]): The list of parameters for the request.
        header DefaultDict[str, str]: Header parameters
    """

    app_id: str
    start_index: int
    end_index: int

    @property
    def header(self) -> Collection[str]:
        return STOREFRONT["headers"]

    @property
    def baseurl(self) -> str:
        return f"https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?id={self.app_id}&displayable-kind=11&startIndex={self.start_index}&endIndex={self.end_index}&sort=1"
