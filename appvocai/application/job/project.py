#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/job/project.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 01:30:04 am                                              #
# Modified   : Wednesday August 28th 2024 01:30:55 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appvocai.core.data import DataClass

# ------------------------------------------------------------------------------------------------ #

@dataclass
class Project(DataClass):
    id: int                            # Unique identifier for the project
    category_id: int                   # Identifier for the category being scraped
    category_name: str                 # Descriptive name for the category (e.g., "Games")
    datatype: str                       # The type of data being scraped (e.g., "Apps", "Reviews")
    scraping_frequency: str             # Frequency of scraping (e.g., "daily", "weekly")
    last_scraped_date: Optional[datetime] = None  # Date of the last scraping job completed
    next_scheduled_job: Optional[datetime] = None  # Date and time for the next scheduled job
    job_count: int = 0                  # Total number of jobs created for the project
    success_rate: float = 0.0           # Percentage of successful scraping jobs
    current_job_status: str = "Idle"    # Status of the most recent job (e.g., "Running", "Completed", "Failed")

