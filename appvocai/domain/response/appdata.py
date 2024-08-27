#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/response/appdata.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 11:13:39 am                                                #
# Modified   : Tuesday August 27th 2024 02:48:25 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass

from aiohttp import ClientResponse

from appvocai.domain.response.base import Response


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ResponseAppData(Response):

    def __post_init__(self) -> None:
        super().__init__()

    def parse_response(self, response: ClientResponse) -> None:
        """Parses the response and populates member variables."""
        super().parse_response()
        content = response.json(content_type=None)
        self.n = content["resultCount"]

# ------------------------------------------------------------------------------------------------ #
