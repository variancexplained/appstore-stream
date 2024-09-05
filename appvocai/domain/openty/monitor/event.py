#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/openty/monitor/event.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday September 5th 2024 12:17:39 am                                             #
# Modified   : Thursday September 5th 2024 06:58:10 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Monitor Base Class"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from appvocai.core.identity import Openty

# ------------------------------------------------------------------------------------------------ #

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class CompteRendu(Openty):
    """Collection of events and methods for calculating metrics and statistics"""

    events: List[Event] = field(default_factory=list)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Event(Openty):
    """Encapsulates metadata for processes and events we monitor."""

    started: Optional[datetime] = None
    ended: Optional[datetime] = None
    status: Optional[int] = None
    duration: float = 0

    def begin(self) -> None:
        """Called at the start of a process"""
        self.started = datetime.now()

    def end(self) -> None:
        """Called at the start of a process"""
        self.ended = datetime.now()
        if self.started:
            self.duration = (self.ended - self.started).total_seconds()
        else:
            msg = "Cannot call end before calling start."
            logger.exception(msg)
            raise RuntimeError(msg)
