#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/database/schema.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday August 30th 2024 02:42:23 am                                                 #
# Modified   : Saturday September 7th 2024 05:13:43 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Module defines the database schema"""
schema = {
    "project": """CREATE TABLE IF NOT EXISTS project(
        project_id VARCHAR(32) NOT NULL,
        project_name VARCHAR(255) NOT NULL,
        data_type ENUM('AppData', 'Review') NOT NULL,
        category_id INTEGER NOT NULL,
        category VARCHAR(64) NOT NULL,
        bookmark INTEGER NOT NULL DEFAULT 0,
        n_jobs INTEGER NOT NULL DEFAULT 0,
        last_job_id VARCHAR(32),
        dt_last_job_started DATETIME,
        dt_last_job_ended DATETIME,
        dt_created DATETIME,
        dt_modified DATETIME,
        last_job_status ENUM("Created", "Scheduled", "In Progress", "Completed", "Failed", "Cancelled"),
        project_status ENUM('Active', 'Idle'),
        PRIMARY KEY (project_id, data_type),
        INDEX idx_data_type (data_type),
        INDEX idx_category_id (category_id),
        INDEX idx_project_status (project_status)
    );
    """,
    "job": """CREATE TABLE IF NOT EXISTS job (
        job_id VARCHAR(32) NOT NULL PRIMARY KEY UNIQUE,
        job_name VARCHAR(255) NOT NULL,
        project_id VARCHAR(32) NOT NULL,
        project_name VARCHAR(255) NOT NULL,
        dataset ENUM('AppData', 'AppReview') NOT NULL,
        category_id INTEGER NOT NULL,
        category VARCHAR(64) NOT NULL,
        bookmark  BIGINT NOT NULL DEFAULT 0,
        dt_created DATETIME NOT NULL,
        dt_scheduled DATETIME,
        dt_started DATETIME,
        dt_modified DATETIME,
        dt_ended DATETIME,
        runtime INTEGER NOT NULL NOT NULL DEFAULT 0,
        job_status ENUM("Created", "Scheduled", "In Progress", "Completed", "Failed", "Cancelled") NOT NULL,
        INDEX idx_category_id (category_id),
        INDEX idx_dataset (dataset),
        INDEX idx_job_status (job_status),
        FOREIGN KEY (project_id) REFERENCES project(project_id)
    );

""",
    "category": """CREATE TABLE IF NOT EXISTS category (
        category_id INTEGER NOT NULL PRIMARY KEY,
        category VARCHAR(128) NOT NULL,
        UNIQUE (category_id),
        INDEX idx_category_id (category_id)
        );""",
    "appdata": """CREATE TABLE IF NOT EXISTS appdata (
        app_id BIGINT NOT NULL PRIMARY KEY,
        app_name VARCHAR(255) NOT NULL,
        app_censored_name VARCHAR(255),
        bundle_id VARCHAR(255),
        description TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        category VARCHAR(128) NOT NULL,
        price DECIMAL(10, 2),
        currency VARCHAR(8),
        rating_average INTEGER NOT NULL,
        rating_average_current_version INTEGER NOT NULL,
        rating_average_current_version_change DECIMAL(3,2),
        rating_average_current_version_pct_change DECIMAL(5,2),
        rating_count INTEGER NOT NULL,
        rating_count_current_version INTEGER NOT NULL,
        developer_id BIGINT NOT NULL,
        developer_name VARCHAR(255) NOT NULL,
        seller_name VARCHAR(255),
        seller_url VARCHAR(255),
        app_content_rating VARCHAR(255),
        content_advisory_rating VARCHAR(255),
        file_size_bytes VARCHAR(255),
        minimum_os_version VARCHAR(255),
        version VARCHAR(8),
        release_date DATETIME NOT NULL,
        release_notes LONGTEXT,
        release_date_current_version DATETIME NOT NULL,
        url_developer_view VARCHAR(255),
        url_app_view VARCHAR(255),
        url_artwork_100 VARCHAR(255),
        url_artwork_512 VARCHAR(255),
        url_artwork_60 VARCHAR(255),
        urls_screenshot_ipad JSON,
        urls_screenshot JSON,
        iphone_support BOOLEAN,
        ipad_support BOOLEAN,
        dt_extracted DATETIME NOT NULL,
        UNIQUE (app_id),
        INDEX idx_category_id (category_id)
        );""",
    "category_app": """CREATE TABLE IF NOT EXISTS category_app (
            app_id BIGINT NOT NULL,
            category_id INTEGER NOT NULL,
            PRIMARY KEY (app_id, category_id),
            FOREIGN KEY (app_id) REFERENCES appdata(app_id),
            FOREIGN KEY (category_id) REFERENCES category(category_id)
        );""",
    "metrics": """CREATE TABLE IF NOT EXISTS metrics (
            project_id VARCHAR(32) NOT NULL,
            job_id VARCHAR(32) NOT NULL,
            task_id VARCHAR(32) NOT NULL,
            operation_id VARCHAR(32) NOT NULL,
            data_type VARCHAR(255) NOT NULL,
            operation_type VARCHAR(255) NOT NULL,
            instances INT NOT NULL,
            dt_started DATETIME NOT NULL,
            dt_ended DATETIME NOT NULL,
            duration FLOAT NOT NULL,
            latency_min FLOAT NOT NULL,
            latency_average FLOAT NOT NULL,
            latency_median FLOAT NOT NULL,
            latency_max FLOAT NOT NULL,
            latency_std FLOAT NOT NULL,
            throughput_min FLOAT NOT NULL,
            throughput_average FLOAT NOT NULL,
            throughput_median FLOAT NOT NULL,
            throughput_max FLOAT NOT NULL,
            throughput_std FLOAT NOT NULL,
            f1 FLOAT,
            f2 FLOAT,
            f3 FLOAT,
            i1 INT,
            i2 INT,
            i3 INT,
            INDEX idx_data_type (data_type),
            INDEX idx_operation_type (operation_type)
);""",
    "error_log": """CREATE TABLE IF NOT EXISTS error_log (
            project_id VARCHAR(32) NOT NULL,              -- ID of the project
            job_id VARCHAR(32) NOT NULL,                  -- ID of the job
            task_id VARCHAR(32) NOT NULL,                 -- ID of the task
            operation_id VARCHAR(32) NOT NULL,            -- ID of the operation
            data_type VARCHAR(100) NOT NULL,      -- The data type (e.g., appdata, reviews)
            operation_type VARCHAR(100) NOT NULL, -- The type of operation (e.g., Extract, Transform, Load)
            error_type VARCHAR(255),              -- The type of error (e.g., network, validation)
            error_code INT,                       -- Specific error code (e.g., HTTP code, custom code)
            error_description TEXT,               -- Detailed description of the error
            dt_error DATETIME DEFAULT CURRENT_TIMESTAMP, -- The datetime the error occurred
            PRIMARY KEY (project_id, job_id, task_id, dt_error)
);
""",
}
