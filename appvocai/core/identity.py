#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/core/identity.py                                                          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday September 4th 2024 07:34:05 pm                                            #
# Modified   : Thursday September 5th 2024 06:37:35 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Identity Module"""
# %%
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appvocai.core.data import DataClass
from appvocai.core.enum import DataType, Env
from appvocai.infra.base.config import Config
from appvocai.infra.identity.idxgen import IDXGen

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Passport(DataClass):
    """
    A data class representing object identity for all objects.

    Attributes:
        data_type (DataType): The type of the entity, which distinguishes between different operation types.
        id (str): A unique identifier for the entity, generated automatically if not provided.
        created (Optional[datetime]): The timestamp when the entity was initially created.
        modified (Optional[datetime]): The timestamp when the entity was last modified.
        environment (Optional[Env]): The environment in which the entity operates (e.g., Development, Production),
                                     determined automatically based on configuration.

    Methods:
        __post_init__: Initializes the entity by generating a unique ID, setting the current timestamp,
                       and determining the environment based on the current configuration.
        size: Calculates the total size of the object, including its attributes.
    """

    id: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    environment: Optional[Env] = None
    data_type: Optional[DataType] = None

    def __post_init__(self) -> None:
        """Initializes the entity after dataclass construction."""
        self.created = datetime.now()
        env = Config().get_environment()
        self.environment = Env.get(value=env)
        if not self.id or not hasattr(self, "id"):
            self.id = IDGen().get_next_id(self)

    def size(self) -> int:
        """Calculate the total size of the object including its attributes."""
        total = sys.getsizeof(self)
        for attr in vars(self).values():
            total += sys.getsizeof(attr)
        return total


# ------------------------------------------------------------------------------------------------ #
class IDGen:
    """
    A class to generate unique identifiers for operational entities (Passport) based on their attributes.

    Attributes:
        _idxgen (IDXGen): An instance of the IDXGen class, used to generate sequential indices.

    Methods:
        get_next_id(passport: Passport) -> str:
            Generates a unique identifier string for the given Passport instance. The identifier is
            constructed using the class name, entity type, creation date, environment, and a daily
            sequential index.
            - If `passport.created` and `passport.environment` are non-null, the method returns a formatted
              string: "classname-entitytype-createddate-environment-seq".
            - If either `created` or `environment` is null, the method logs an exception and raises a
              RuntimeError.

    Example:
        passport_idx = PassportIDX()
        unique_id = passport_idx.get_next_id(some_passport_instance)
        print(unique_id)
    """

    def __init__(self, idxgen_cls: type[IDXGen] = IDXGen) -> None:
        """Initializes the PassportIDX with an instance of IDXGen for generating sequential indices."""
        self._idxgen = idxgen_cls()

    def get_next_id(self, passport: Passport) -> str:
        """
        Generates the next unique identifier for the given Passport instance.

        Args:
            passport (Passport): The operational entity for which the ID is being generated.

        Returns:
            str: A unique identifier string in the format
            "classname-entitytype-createddate-environment-seq".

        Raises:
            RuntimeError: If `passport.created` or `passport.environment` is None.

        Example:
            passport_idx = PassportIDX()
            unique_id = passport_idx.get_next_id(some_passport_instance)
            print(unique_id)  # Outputs something like "classname-entitytype-20240904-env-001"
        """
        if passport.created and passport.environment and passport.data_type:
            return f"{passport.__class__.__name__.lower()}-{passport.data_type}-{passport.created.strftime('%Y%m%d')}-{passport.environment.value}-{self._idxgen.next_idx}"
        elif passport.created and passport.environment:
            return f"{passport.__class__.__name__.lower()}-{passport.created.strftime('%Y%m%d')}-{passport.environment.value}-{self._idxgen.next_idx}"
        else:
            msg = "Operations Entity must have non-null values for created and environment."
            logging.exception(msg)
            raise RuntimeError(msg)
