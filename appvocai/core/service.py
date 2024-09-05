#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/core/service.py                                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 11:33:51 pm                                                 #
# Modified   : Wednesday September 4th 2024 08:42:08 pm                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC
from datetime import datetime
from typing import Any, Dict, Union

import pandas as pd

from appvocai.core.data import IMMUTABLE_TYPES, SEQUENCE_TYPES


# ------------------------------------------------------------------------------------------------ #
# mypy: allow-any-generics
# ------------------------------------------------------------------------------------------------ #
class Service(ABC):
    """Abstract base class for application, domain, and infrastructure services."""

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
        elif isinstance(v, datetime):
            return v
        elif isinstance(v, dict):
            return v
        elif hasattr(v, "as_dict"):
            return v.as_dict()
        else:
            return dict()

    def as_df(self) -> Any:
        """Returns the project in DataFrame format"""
        d = self.as_dict()
        return pd.DataFrame(data=d, index=[0])
