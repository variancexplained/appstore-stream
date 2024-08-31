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
# Modified   : Friday August 30th 2024 07:03:56 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Module defines the database schema"""
schema = {
    "category":
        """CREATE TABLE category (
        id INTEGER NOT NULL PRIMARY KEY,
        category VARCHAR(128) NOT NULL,
        UNIQUE (id) -- Ensures the id is unique
        );""",
    "appdata":
        """CREATE TABLE appdata (
        app_id BIGINT NOT NULL PRIMARY KEY,
        app_name VARCHAR(255) NOT NULL,
        app_censored_name VARCHAR(255),
        bundle_id VARCHAR(255),
        description TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        category VARCHAR(128) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        currency VARCHAR(8) NOT NULL,
        rating_average INTEGER NOT NULL,
        rating_average_current_version INTEGER NOT NULL,
        rating_average_current_version_change DECIMAL(3,2) NOT NULL,
        rating_average_current_version_pct_change DECIMAL(5,2) NOT NULL,
        rating_count INTEGER NOT NULL,
        rating_count_current_version INTEGER NOT NULL,
        developer_id BIGINT NOT NULL,
        developer_name VARCHAR(255) NOT NULL,
        seller_name VARCHAR(255) NOT NULL,
        app_content_rating VARCHAR(255) NOT NULL,
        content_advisory_rating VARCHAR(255) NOT NULL,
        file_size_bytes VARCHAR(255),
        minimum_os_version VARCHAR(255),
        version VARCHAR(8) NOT NULL,
        release_date DATETIME NOT NULL,
        release_notes LONGTEXT NOT NULL,
        release_date_current_version DATETIME NOT NULL,
        url_developer_view VARCHAR(255),
        url_seller VARCHAR(255),
        url_app_view VARCHAR(255),
        url_artwork_100 VARCHAR(255),
        url_artwork_512 VARCHAR(255),
        url_artwork_60 VARCHAR(255),
        urls_screenshot_ipad JSON,
        urls_screenshot_iphone JSON,
        extract_date DATETIME NOT NULL,
        UNIQUE (app_id),
        INDEX idx_category_id (category_id)
        );""",
    "category_app":
        """CREATE TABLE category_app (
            app_id BIGINT NOT NULL,
            category_id INTEGER NOT NULL,
            PRIMARY KEY (app_id, category_id),
            FOREIGN KEY (app_id) REFERENCES appdata(app_id),
            FOREIGN KEY (category_id) REFERENCES category(id)
        );"""

}