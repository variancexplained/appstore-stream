#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/response/review.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 02:00:33 pm                                                #
# Modified   : Tuesday August 27th 2024 02:48:31 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from aiohttp import ClientResponse

from appvocai.domain.response.base import Response


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ResponseAppData(Response):


    def __post_init__(self) -> None:
        super().__init__()

    def parse_response(self, response: ClientResponse) -> None:
        """Parses the response object and sets the response-related member variables.

        Args:
            response (ClientResponse): The response object containing relevant metadata.
        """
        # Call the base class method to set default values
        super().parse_response(response)

        # Set response metadata
        content = response.json()
        self.n = len(content["userReviewList"])  # Assuming response.data holds the records

