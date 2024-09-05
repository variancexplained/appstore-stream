#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/base.py                                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday September 4th 2024 07:34:05 pm                                            #
# Modified   : Thursday September 5th 2024 12:45:50 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Operation Base Module"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from appvocai.core.data import DataClass
from appvocai.infra.base.config import Config


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Entity(DataClass):
    """Defines a base class for appdata and appreview classes."""


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Sensor(DataClass):
    """Base class for subclasses that monitor and collect data on processes."""

    id: Optional[str] = None
    created: Optional[datetime] = None
    environment: Optional[Env] = None
    version: str = "0.1.0"
    tags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initializes the entity after dataclass construction."""
        self.created = datetime.now()
        env = Config().get_environment()
        self.environment = Env.get(value=env)
        if not self.id or not hasattr(self, "id"):
            self.id = OpentyIDX().get_next_id(self)
