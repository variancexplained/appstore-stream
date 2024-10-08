#!/usr/bin/bash
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /scripts/monitor/prometheus/start_test.sh                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 05:31:30 pm                                                   #
# Modified   : Saturday August 31st 2024 02:42:41 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
# Prometheus binary
PROMETHEUS_INSTALL_PATH="/usr/local/bin/prometheus"
# Test Config File
PROMETHEUS_CONFIG_FILE="config/prometheus_test.yaml"
# Default Data Directory
PROMETHEUS_DATA_DIR="metrics"
# Start Prometheus with the custom configuration file
$PROMETHEUS_INSTALL_PATH --config.file=$PROMETHEUS_CONFIG_FILE --storage.tsdb.path=$PROMETHEUS_DATA_DIR --web.enable-admin-api
