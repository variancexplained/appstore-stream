#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_infra/test_repo/test_metrics_repo/test_extract_metrics_repo.py          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 08:33:31 am                                               #
# Modified   : Saturday September 7th 2024 11:10:51 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
import random
from datetime import datetime, timedelta

import pandas as pd
import pytest

from appvocai.core.enum import DataType, StageType
from appvocai.domain.monitor.extract import ExtractMetrics
from appvocai.infra.repo.monitor.extract import ExtractMetricsRepo

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# mypy: ignore-errors
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"

stage_types = [StageType.EXTRACT, StageType.LOAD, StageType.TRANSFORM]
data_types = [DataType.APPDATA, DataType.APPREVIEW]

NUM_METRICS = 16
NUM_METRICS_PER_TASK = 4
NUM_METRICS_PER_JOB = 4


class MetricsGen:
    def __init__(self):
        self.job_id = 0
        self.task_id = 0
        self.request_id = 0

    def gen(self):
        self.job_id += 1
        self.task_id += 1
        self.request_id += 1
        return ExtractMetrics(
            job_id=self.job_id % NUM_METRICS_PER_JOB,
            data_type=random.choice(data_types),
            task_id=self.task_id % NUM_METRICS_PER_TASK,
            stage_type=random.choice(stage_types),
            request_id=self.request_id,
            dt_started=datetime.now() - timedelta(days=random.randint(0, 3)),
            dt_ended=datetime.now() - timedelta(days=random.randint(4, 6)),
            duration=random.randint(1000, 10000),
            requests=random.randint(10, 100),
            latency_min=random.random(),
            latency_average=random.random(),
            latency_median=random.random(),
            latency_max=random.random(),
            latency_std=random.random(),
            throughput_min=random.random(),
            throughput_average=random.random(),
            throughput_median=random.random(),
            throughput_max=random.random(),
            throughput_std=random.random(),
            speedup=random.randint(1, 5),
            size=random.random() * 1000,
        )


@pytest.mark.extract_metrics
@pytest.mark.metrics
class TestExtractMetrics:  # pragma: no cover
    # ============================================================================================ #
    def test_setup(self, caplog, container) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        query = "DELETE FROM metrics;"
        params = {}
        with db as database:
            database.execute(query=query, params=params)
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_add(self, caplog, container) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        metrics_gen = MetricsGen()
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        for i in range(NUM_METRICS):
            metrics = metrics_gen.gen()
            repo.add(metrics=metrics)

        assert len(repo) == NUM_METRICS

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_get_job_metrics(self, container, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        for i in range(NUM_METRICS_PER_JOB):
            metrics = repo.get_job_metrics(job_id=i)
            assert len(metrics) == NUM_METRICS_PER_JOB
            assert isinstance(metrics, pd.DataFrame)
            logging.debug(metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_get_task_metrics(self, container, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        for i in range(NUM_METRICS_PER_TASK):
            metrics = repo.get_task_metrics(task_id=i)
            assert len(metrics) == NUM_METRICS_PER_TASK
            assert isinstance(metrics, pd.DataFrame)
            logging.debug(metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_get_stage_type_metrics(self, container, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        metrics = repo.get_stage_type_metrics(stage_type=StageType.EXTRACT)
        assert isinstance(metrics, pd.DataFrame)
        logging.debug(metrics)

        metrics = repo.get_stage_type_metrics(stage_type=StageType.TRANSFORM)
        assert isinstance(metrics, pd.DataFrame)
        logging.debug(metrics)

        metrics = repo.get_stage_type_metrics(stage_type=StageType.LOAD)
        assert isinstance(metrics, pd.DataFrame)
        logging.debug(metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_get_data_type_metrics(self, container, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        metrics = repo.get_data_type_metrics(data_type=DataType.APPDATA)
        assert isinstance(metrics, pd.DataFrame)
        logging.debug(metrics)

        metrics = repo.get_data_type_metrics(data_type=DataType.APPREVIEW)
        assert isinstance(metrics, pd.DataFrame)
        logging.debug(metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_remove_job_metrics_NOT_APPROVED(self, container, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        repo.remove_job_metrics(job_id=1)
        metrics = repo.get_job_metrics(job_id=1)
        assert isinstance(metrics, pd.DataFrame)
        assert len(metrics) == NUM_METRICS_PER_JOB
        logging.debug(metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_remove_job_metrics_APPROVED(self, container, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        repo.remove_job_metrics(job_id=1)
        metrics = repo.get_job_metrics(job_id=1)
        assert isinstance(metrics, pd.DataFrame)
        assert len(metrics) == 0
        logging.debug(metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_remove_ALL_metrics_NOT_APPROVED(self, container, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        repo.remove_all()
        metrics = repo.get_all()
        assert isinstance(metrics, pd.DataFrame)
        assert len(metrics) == NUM_METRICS - NUM_METRICS_PER_JOB
        logging.debug(metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_remove_ALL_metrics_APPROVED(self, container, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        db = container.db.mysql()
        repo = ExtractMetricsRepo(database=db)
        repo.remove_all()
        metrics = repo.get_all()
        assert isinstance(metrics, pd.DataFrame)
        assert len(metrics) == 0

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
