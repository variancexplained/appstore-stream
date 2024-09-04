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
# Modified   : Sunday September 1st 2024 06:58:23 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Module defines the database schema"""
schema = {
    "category":
        """CREATE TABLE category (
        category_id INTEGER NOT NULL PRIMARY KEY,
        category VARCHAR(128) NOT NULL,
        UNIQUE (category_id),
        INDEX idx_category_id (category_id)
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
            FOREIGN KEY (category_id) REFERENCES category(category_id)
        );"""

}