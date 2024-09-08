#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/identity/idxgen.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday September 4th 2024 09:51:14 pm                                            #
# Modified   : Saturday September 7th 2024 05:04:02 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
# %%
import logging
import os
import shelve
from datetime import datetime

from appvocai.infra.base.config import Config


# ------------------------------------------------------------------------------------------------ #
class IDXGen:
    """
    A class that generates a sequential index value based on the current date and persists it using `shelve`.

    The index resets to 1 whenever the date changes, ensuring unique indices per day. The index and last recorded date
    are stored in a persistent shelve file, allowing the class to maintain the state across different executions.

    Attributes:
    -----------
    __directory_key : str
        A private class attribute that holds the name of the environment variable which contains the directory path
        for storing the shelve file.

    _logger : logging.Logger
        A logger instance used to log information and errors during file path setup and index generation.

    _shelve_file : str
        The file path where the shelve file is stored. This is determined from the environment variable.

    Properties:
    -----------
    today : str
        Returns the current date as a string in the format 'YYYYMMDD'.

    next_idx : str
        Returns the next sequential index for the current date in the format 'YYYYMMDD-INDEX'.
        If the date has changed, the index resets to 1 for the new date.

    Methods:
    --------
    _get_filepath() -> str
        Determines the file path for the shelve file based on the environment variable defined by `__directory_key`.
        If the directory does not exist, it creates it. Raises an error if the environment variable is not set or
        if any file/directory creation issues occur.
    """

    __directory_key = (
        "OPS_DIRECTORY"  # Environment variable containing the ops directory
    )

    def __init__(self) -> None:
        """
        Initializes the IDXGen instance by setting up the logger and determining the shelve file path.

        Raises:
        -------
        Exception
            If there is an issue with setting up the shelve file path, logs the error and re-raises the exception.
        """
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        try:
            self._shelve_file = self._get_filepath()
        except Exception as e:
            self._logger.error(f"Failed to set up shelve file path: {e}")
            raise

    @property
    def today(self) -> str:
        """Returns the current date as a string in YYYYMMDD format."""
        return datetime.now().strftime("%Y%m%d")

    @property
    def next_idx(self) -> str:
        """
        Retrieves the next sequential index for the current date. If the date has changed since the last retrieval,
        the index is reset to 1. Otherwise, the index is incremented.

        Returns:
        --------
        str
            The next index in the format 'YYYYMMDD-INDEX'.

        Raises:
        -------
        Exception
            If there is an error opening or modifying the shelve file, logs the error and re-raises the exception.
        """
        try:
            with shelve.open(self._shelve_file) as db:
                last_date = db.get("last_date", None)
                if last_date == self.today:
                    last_idx = db.get("idx", 0)
                    next_idx = int(last_idx) + 1
                    db["idx"] = next_idx
                else:
                    # Reset the index if the date has changed
                    next_idx = 1
                    db["last_date"] = self.today
                    db["idx"] = next_idx
                    self._logger.info(
                        f"Date changed, index reset to: {next_idx} for new date: {self.today}"
                    )
                return f"{datetime.now().strftime('%Y%m%d')}-{next_idx}"
        except Exception as e:
            self._logger.error(f"Failed to get next index: {e}")
            raise

    def _get_filepath(self) -> str:
        """
        Retrieves the file path for storing the shelve file. The path is determined using an environment variable.

        Returns:
        --------
        str
            The full file path where the shelve file will be stored.

        Raises:
        -------
        EnvironmentError
            If the environment variable containing the directory path is not set.
        OSError
            If there is an error creating the directory or accessing the file path.
        """
        try:
            directory = Config().get_env_var(self.__directory_key)
            if not directory:
                raise EnvironmentError(
                    f"Environment variable {self.__directory_key} is not set."
                )
            os.makedirs(directory, exist_ok=True)
            return os.path.join(directory, "idxgen")
        except OSError as e:
            self._logger.error(f"Failed to create directory or file path: {e}")
            raise


# ------------------------------------------------------------------------------------------------ #
# idxgen = IDXGen()
# print(idxgen.next_idx)
