#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/web/monitor.py                                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday September 5th 2024 01:16:16 am                                             #
# Modified   : Thursday September 5th 2024 06:58:10 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Web Monitoring Module"""
from dataclasses import dataclass, field
from typing import List, Optional

from appvocai.domain.openty.monitor.event import CompteRendu, Event


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ASessionCR(CompteRendu):
    session: Optional[Event] = None
    requests: List[Event] = field(default_factory=list)

    def set_session_event(self, session: Event) -> None:
        self.session = session

    def add_request_event(self, request: Event) -> None:
        self.requests.append(request)
