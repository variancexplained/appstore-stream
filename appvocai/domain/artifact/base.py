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
# Modified   : Sunday September 8th 2024 08:20:23 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Stage Base Module"""
from abc import ABC
from dataclasses import dataclass

from appvocai.application.orchestration.context import JobContext


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Artifact(ABC):
    """Defines a base class for the classes of objects passed among Tasks."""

    context: JobContext
