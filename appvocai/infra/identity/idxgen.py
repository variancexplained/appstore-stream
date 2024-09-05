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
# Modified   : Thursday September 5th 2024 06:37:29 am                                             #
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
    __directory_key = (
        "OPS_DIRECTORY"  # Environment variable containing the ops directory
    )

    def __init__(self) -> None:
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
    def next_idx(self) -> int:
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
                return next_idx
        except Exception as e:
            self._logger.error(f"Failed to get next index: {e}")
            raise

    def _get_filepath(self) -> str:
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
