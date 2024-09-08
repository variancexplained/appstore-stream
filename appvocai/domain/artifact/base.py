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
# Modified   : Saturday September 7th 2024 06:25:40 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Operation Base Module"""
from abc import ABC
from dataclasses import dataclass

from appvocai.infra.identity.passport import ArtifactPassport, OperationPassport


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Artifact(ABC):
    """Defines a base class for the classes of objects passed among Tasks."""

    def __init__(self, operation_passport: OperationPassport) -> None:
        self.passport = ArtifactPassport(self, operation_passport)
