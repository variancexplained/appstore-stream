#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.12.3                                                                              #
# Filename   : /appvocai/ui/print.py                                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday May 6th 2024 11:07:56 pm                                                     #
# Modified   : Sunday September 1st 2024 06:17:01 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from datetime import date, datetime
from typing import Any, Dict

import numpy as np
import pandas as pd

# ------------------------------------------------------------------------------------------------ #
IMMUTABLE_TYPES: tuple = (
    str,
    int,
    float,
    bool,
    np.int16,
    np.int32,
    np.int64,
    np.int8,
    np.uint8,
    np.uint16,
    np.float16,
    np.float32,
    np.float64,
    np.float128,
    np.bool_,
    datetime,
    date,
)


class Printer:
    """Class for printing in various formats.

    Attributes
    ----------
    _width : int
        The width of the printed output.
    """

    def __init__(self, width: int = 80) -> None:
        """
        Initializes the Printer with a specified width.

        Args:
            width (int): The width of the printed output. Default is 80.
        """
        self._width = width

    def print_header(self, title: str) -> None:
        """
        Prints a formatted header.

        Args:
            title (str): The title to be printed in the header.
        """
        breadth = self._width - 4
        header = f"\n\n# {breadth * '='} #\n"
        header += f"#{title.center(self._width - 2, ' ')}#\n"
        header += f"# {breadth * '='} #\n"
        print(header)

    def print_trailer(self) -> None:
        """
        Prints a formatted trailer.
        """
        breadth = self._width - 4
        trailer = f"\n\n# {breadth * '='} #\n"
        print(trailer)

    def print_dict(self, title: str, data: Dict[str,Any]) -> None:
        """
        Prints a dictionary in a formatted manner.

        Args:
            title (str): The title to be printed above the dictionary.
            data (dict): The dictionary to be printed.
        """
        breadth = int(self._width / 2)
        s = f"\n\n{title.center(self._width, ' ')}"
        for k, v in data.items():
            if isinstance(v, IMMUTABLE_TYPES):
                if isinstance(v, float) or isinstance(v, int):
                    v = f"{v:,}"
                s += f"\n{k.rjust(breadth, ' ')} | {v}"
        s += "\n\n"
        print(s)

    def print_dataframe_as_dict(
        self, df: pd.DataFrame, title: str, list_index: int = 0
    ) -> None:
        """
        Prints a DataFrame as a dictionary.

        Converts a DataFrame to a list of dictionaries, and prints the designated dictionary
        from the list index.

        Args:
            df (pd.DataFrame): A pandas DataFrame object.
            title (str): The title to be printed above the dictionary.
            list_index (int): The index within the list of dictionaries (rows) to print. Default is 0.
        """
        d = df.to_dict("records")[0]
        self.print_dict(title=title, data=d)
