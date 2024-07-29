#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/appdata/control.py                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 01:51:56 am                                                   #
# Modified   : Monday July 29th 2024 01:58:38 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Control Module"""
from appstorestream.application.appdata.job import AppDataJob
from appstorestream.application.base.control import Controller
from appstorestream.application.base.project import Project


# ------------------------------------------------------------------------------------------------ #
class AppDataController(Controller):
    def get_job(self, project: Project) -> AppDataJob:
        return AppDataJob(project=project)
