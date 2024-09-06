#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/operation/transform.py                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:46:38 pm                                               #
# Modified   : Friday September 6th 2024 05:27:51 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import logging
from abc import abstractmethod
from datetime import datetime
from typing import Generic, List, TypeVar

from dependency_injector.wiring import Provide, inject
from pydantic import ValidationError

from appvocai.application.observer.transform import ObserverTransformMetrics
from appvocai.application.operation.base import Task
from appvocai.container import AppVoCAIContainer
from appvocai.domain.content.appdata import AppData, RawAppData
from appvocai.domain.content.base import Entity
from appvocai.domain.metrics.transform import MetricsTransform
from appvocai.domain.response.response import ResponseAsync

# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T", bound="Entity")


# ------------------------------------------------------------------------------------------------ #
class TransformOperation(Task, Generic[T]):
    """
    A base class for executing asynchronous transform tasks.

    This class handles the process of converting asynchronous responses to entity
    i.e. AppData, AppReview objects, metrics collection, validation, and observer
    notification. It is designed to be subclassed for specific types of transform tasks.

    Attributes:
        _observer (ObserverTransformMetrics): The observer that monitors and responds to
            changes in metrics.
    """

    @inject
    def __init__(self, observer: ObserverTransformMetrics) -> None:
        """
        Initializes the TaskTransform class with the specified dependency.

        Args:
            observer (ObserverTransformMetrics): The observer that will monitor and
                report on metrics.

        """
        self._observer = observer
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def run(self, async_response: ResponseAsync) -> List[T]:
        """ """
        metrics = MetricsTransform()

        # Collect pre-execution metrics
        metrics.pre()

        # Conducts validation, updates metrics and transforms the data into a list of AppData Entities
        appdata_list = self.transform(async_response=async_response, metrics=metrics)

        # Collect post-execution metrics
        metrics.post()

        # Compute and finalize metrics
        metrics.validate()

        # Notify the observer with the finalized metrics
        self._observer.notify(metrics=metrics)

        return appdata_list

    @abstractmethod
    def transform(
        self, async_response: ResponseAsync, metrics: MetricsTransform
    ) -> List[T]:
        """Performs data specific transformations."""

    def parse_date(self, datetime_string: str) -> datetime:
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------------------------------------ #
class TransformOperationAppData(TaskTransform[AppData]):
    """
    A specialized TaskTransform class for handling AsyncRequestAppData types.

    This class uses a specific observer tailored for app data transformion tasks.
    """

    @inject
    def __init__(
        self,
        observer: ObserverTransformMetrics = Provide[
            AppVoCAIContainer.observe.appdata_transform_observer
        ],
    ) -> None:
        """
        Initializes the TaskTransformAppData class with a specific observer.

        Args:
            observer (ObserverTransformMetrics): The observer specifically set up for
                app data transformion tasks.
        """
        super().__init__(observer=observer)

    def transform(
        self, async_response: ResponseAsync, metrics: MetricsTransform
    ) -> List[AppData]:
        """Conducts validation, updates metrics and transforms the data into a list of AppData Entities"""
        appdata_list = []

        # Extract the response content from the async_response object.
        for response in async_response.responses:
            for content in response.content:
                # Increment number of records in
                metrics.records_in += 1
                ## Validate appdata.
                try:
                    raw_data = RawAppData.create(content=content)
                    appdata = self._parse_content(raw_data=raw_data)
                    appdata_list.append(appdata)
                    metrics.records_out += 1

                except ValidationError as e:
                    metrics.errors += len(e.errors())
                    for error in e.errors():
                        msg = f"variable: {error['loc']}, Error: {error['msg']}  Type: {error['type']}"
                        self._logger.error(msg=msg)
        return appdata_list

    def _parse_content(self, raw_data: RawAppData) -> AppData:
        # Devices
        search_iphone = "iPhone"
        search_ipad = "iPad"
        iphone_support = (
            any(search_iphone in device for device in raw_data.supported_devices)
            if raw_data.supported_devices
            else False
        )
        ipad_support = (
            any(search_ipad in device for device in raw_data.supported_devices)
            if raw_data.supported_devices
            else False
        )

        # Rating Change Current Version
        rating_change = (
            raw_data.rating_average_current_version - raw_data.rating_average
        )
        rating_change_pct = rating_change / raw_data.rating_average * 100

        # Construct the AppData entity
        appdata = AppData(
            app_id=raw_data.app_id,
            app_name=raw_data.app_name,
            app_censored_name=raw_data.app_censored_name,
            bundle_id=raw_data.bundle_id,
            description=raw_data.description,
            category_id=raw_data.category_id,
            category=raw_data.category,
            rating_average=raw_data.rating_average,
            rating_average_current_version=raw_data.rating_average_current_version,
            rating_count=raw_data.rating_count,
            rating_count_current_version=raw_data.rating_count_current_version,
            developer_id=raw_data.developer_id,
            developer_name=raw_data.developer_name,
            release_date=raw_data.release_date,
            release_date_current_version=raw_data.release_date_current_version,
            categories=raw_data.categories,
            price=raw_data.price,
            currency=raw_data.currency,
            rating_average_current_version_change=rating_change,
            rating_average_current_version_pct_change=rating_change_pct,
            url_developer_view=raw_data.url_developer_view,
            seller_name=raw_data.seller_name,
            seller_url=raw_data.seller_url,
            app_content_rating=raw_data.app_content_rating,
            content_advisory_rating=raw_data.content_advisory_rating,
            file_size_bytes=raw_data.file_size_bytes,
            minimum_os_version=raw_data.minimum_os_version,
            version=raw_data.version,
            release_notes=raw_data.release_notes,
            iphone_support=iphone_support,
            ipad_support=ipad_support,
            url_artwork_100=raw_data.url_artwork_100,
            url_app_view=raw_data.url_app_view,
            url_artwork_512=raw_data.url_artwork_512,
            url_artwork_60=raw_data.url_artwork_60,
            urls_screenshot_ipad=raw_data.urls_screenshot_ipad,
            urls_screenshot=raw_data.urls_screenshot,
            extract_date=datetime.now(),
        )
        return appdata


# ------------------------------------------------------------------------------------------------ #
class TransformOperationAppReview(TaskTransform):
    """
    A specialized TaskTransform class for handling AsyncRequestAppReview types.

    This class uses a specific observer tailored for app review transformion tasks.
    """

    @inject
    def __init__(
        self,
        observer: ObserverTransformMetrics = Provide[
            AppVoCAIContainer.observe.appreview_transform_observer
        ],
    ) -> None:
        """
        Initializes the TaskTransformAppReview class with a specific observer.

        Args:
            observer (ObserverTransformMetrics): The observer specifically set up for
                app review transformion tasks.
        """
        super().__init__(observer=observer)

    def transform(
        self, async_response: ResponseAsync, metrics: MetricsTransform
    ) -> List[Entity]:
        """Performs data specific transformations."""
