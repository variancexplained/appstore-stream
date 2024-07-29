#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/container.py                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 04:17:11 am                                                 #
# Modified   : Sunday July 28th 2024 02:01:06 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Framework Dependency Container"""
import logging
import logging.config  # pragma: no cover

from dependency_injector import containers, providers

from appstorestream.infra.database.mysql import MySQLDatabase
from appstorestream.infra.repo.appdata import AppDataRepo
from appstorestream.infra.repo.job import JobRepo
from appstorestream.infra.repo.project import ProjectRepo
from appstorestream.infra.web.asession import ASessionAppData, ASessionReview
from appstorestream.infra.web.throttle import AThrottle


# ------------------------------------------------------------------------------------------------ #
#                                        LOGGING                                                   #
# ------------------------------------------------------------------------------------------------ #
class LoggingContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )

# ------------------------------------------------------------------------------------------------ #
#                                      PERSISTENCE                                                 #
# ------------------------------------------------------------------------------------------------ #
class PersistenceContainer(containers.DeclarativeContainer):

    database = providers.Singleton(MySQLDatabase)

    appdata_repo = providers.Singleton(AppDataRepo, database=database)

    job_repo = providers.Singleton(JobRepo, database=database)

    project_repo = providers.Singleton(ProjectRepo)


# ------------------------------------------------------------------------------------------------ #
#                                         WEB                                                      #
# ------------------------------------------------------------------------------------------------ #
class WebContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    athrottle = providers.Singleton(AThrottle,
                                    min_rate=config.request.athrottle.min_rate,
                                    base_rate=config.request.athrottle.base_rate,
                                    max_rate=config.request.athrottle.max_rate,
                                    temperature=config.request.athrottle.temperature,
                                    window_size=config.request.athrottle.window_size,
                                    burn_in=config.request.athrottle.burn_in,
                                    )
    asession_appdata = providers.Singleton(ASessionAppData,
                                           throttle=athrottle,
                                           max_concurrency=config.request.asession.max_concurrency,
                                           retries=config.request.asession.retries,
                                           timeout=config.request.asession.timeout,
                                           )

    asession_review = providers.Singleton(ASessionReview,
                                           throttle=athrottle,
                                           max_concurrency=config.request.asession.max_concurrency,
                                           retries=config.request.asession.retries,
                                           timeout=config.request.asession.timeout,
                                           )
# ------------------------------------------------------------------------------------------------ #
#                                       FRAMEWORK                                                  #
# ------------------------------------------------------------------------------------------------ #
class AppStoreStreamContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    logs = providers.Container(LoggingContainer, config=config)

    data = providers.Container(PersistenceContainer)

    web = providers.Container(WebContainer, config=config)