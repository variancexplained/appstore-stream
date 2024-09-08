#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/operation/base.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 04:22:03 pm                                              #
# Modified   : Saturday September 7th 2024 05:55:44 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from appvocai.domain.artifact.base import Artifact
from appvocai.infra.identity.passport import ArtifactPassport, TaskPassport

# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T")


# ------------------------------------------------------------------------------------------------ #
class Operation(ABC, Generic[T]):
    """Abstract base class for Task objects."""

    @abstractmethod
    def run(
        self, task_passport: TaskPassport, artifact: Artifact
    ) -> Optional[Artifact]:
        """Executes the task."""

    @property
    def operation_type(self) -> str:
        """Returns the operation type"""
        return self.__class__.__name__

    def check_in(self, task_passport: TaskPassport, artifact: Artifact) -> Artifact:
        artifact.passport = ArtifactPassport(
            owner=artifact, task_passport=task_passport
        )
        artifact.passport.operation_type = (
            self.operation_type if self.operation_type else None
        )
        return artifact

    @abstractmethod
    def check_out(self, artifact: T) -> T:
        """Prepares content for the next stage"""
