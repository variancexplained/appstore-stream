#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/response/review.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 02:00:33 pm                                                #
# Modified   : Sunday September 1st 2024 01:57:37 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from aiohttp import ClientResponse

from appvocai.domain.request.base import Request
from appvocai.domain.response.base import Response


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ResponseAppReview(Response):
    n: int = 0 # Number of records in response

    def parse_request(self, request: Request) -> None:
        super().parse_request(request)
        self.request_type = "review"

    async def parse_response(self, response: ClientResponse) -> None:
        """Parses the response and populates member variables."""
        await super().parse_response(response=response)
        content = await response.json(content_type=None)
        self.n = len(content.get("userReviewList",0))

