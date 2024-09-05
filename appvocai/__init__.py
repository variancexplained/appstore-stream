#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/__init__.py                                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday July 24th 2024 12:42:51 am                                                #
# Modified   : Thursday September 5th 2024 08:35:06 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Identity Module"""
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from appvocai.core.data import IMMUTABLE_TYPES, SEQUENCE_TYPES
from appvocai.core.enum import Category, DataType, Env
from appvocai.infra.base.config import Config
from appvocai.infra.identity.idxgen import IDXGen

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
idxgen = IDXGen()


# ------------------------------------------------------------------------------------------------ #
class Passport:
    """
    A class that encapsulates identity and metadata information for an object instance.

    The `Passport` class generates a unique identifier for an object, records the time of creation,
    and captures the environment in which the object is created. It inspects the attributes of the
    owner object for specific metadata such as `category`, `data_type`, and the `created_by` reference
    to another `Passport`.

    Attributes:
        id (str): A unique identifier generated for the owner object.
        name (str): The class name of the owner object, if available.
        created (datetime): The timestamp of when the Passport was created.
        environment (Env): The environment in which the Passport was created, derived from configuration.
        category (Optional[Category]): The category of the owner object, if found.
        data_type (Optional[DataType]): The data type of the owner object, if found.
        created_by (Optional[Passport]): The Passport of the creator object, if found.
    """

    def __init__(self, owner: Any) -> None:
        """
        Initializes the Passport with identity and metadata from the owner object.

        The initializer generates a unique ID, sets the creation timestamp, and determines the environment
        from configuration settings. It then checks the owner's attributes for specific metadata such as
        `category`, `data_type`, and `created_by`.

        Args:
            owner (Any): The object for which the Passport is being created. The Passport will extract
                        metadata from this object, including the class name and any relevant attributes.
        """
        self.id = idxgen.next_idx

        # Extract class name if available.
        self.name = None
        # Check if owner is an instance of a user-defined class
        if isinstance(owner, object) and not isinstance(
            owner, (int, str, float, tuple, list, dict, set)
        ):
            self.name = owner.__class__.__name__

        self.created = datetime.now()

        # Get current environment from config and obtain an Env instance.
        env = Config().get_environment()
        self.environment = Env.get(value=env)
        # Category and Datatype will be added from object attributes.
        self.category: Optional[Category] = None
        self.data_type: Optional[DataType] = None

        # Check only the owner object's attributes
        self._search_attributes(owner)

    def __repr__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                "{}={!r}".format(k, v)
                for k, v in self.__dict__.items()
                if type(v) in IMMUTABLE_TYPES
            ),
        )

    def __str__(self) -> str:
        width = 32
        breadth = width * 2
        s = f"\n\n{self.__class__.__name__.center(breadth, ' ')}"
        d = self.as_dict()
        for k, v in d.items():
            if type(v) in IMMUTABLE_TYPES:
                s += f"\n{k.rjust(width,' ')} | {v}"
        s += "\n\n"
        return s

    def _search_attributes(self, instance: Any) -> None:
        """
        Searches only the top-level attributes of the given instance for specific metadata.

        This method checks the `__dict__` of the instance to find attributes named `category`,
        `data_type`, and `created_by`. It does not search recursively into nested objects or collections.

        Args:
            instance (Any): The object instance whose attributes are being searched for metadata.
        """
        if hasattr(instance, "__dict__"):
            for key, value in instance.__dict__.items():
                if key == "category":
                    self.category = value
                elif key == "data_type":
                    self.data_type = value
                elif key == "created_by" and isinstance(value, Passport):
                    self.created_by = value

    def as_dict(self) -> Dict[str, Union[str, int, float, datetime, None]]:
        """Returns a dictionary representation of the the Config object."""
        return {
            k: self._export_config(v)
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    @classmethod
    def _export_config(
        cls,
        v: Any,
    ) -> Any:  # pragma: no cover
        """Returns v with Configs converted to dicts, recursively."""
        if isinstance(v, IMMUTABLE_TYPES):
            return v
        elif isinstance(v, SEQUENCE_TYPES):
            return type(v)(map(cls._export_config, v))
        elif isinstance(v, dict):
            return v
        elif hasattr(v, "as_dict"):
            return v.as_dict()
        elif isinstance(v, Enum):
            return v.value
        elif isinstance(v, datetime):
            return v.isoformat()
        else:
            return dict()
