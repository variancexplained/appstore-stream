#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/artifact/base.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday September 4th 2024 07:34:05 pm                                            #
# Modified   : Friday September 6th 2024 04:41:38 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Operation Base Module"""
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Optional

from appvocai.core.enum import OperationType
from appvocai.infra.identity.passport import ArtifactPassport, TaskPassport


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Artifact(ABC):
    """Defines a base class for the classes of objects passed among Tasks."""

    def __init__(
        self, *args: Any, task_passport: TaskPassport, **kwargs: Dict[str, Any]
    ) -> None:
        self.passport = ArtifactPassport(self, task_passport)
        self.operation_type: Optional[OperationType] = None
