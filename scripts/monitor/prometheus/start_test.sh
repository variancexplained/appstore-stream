#!/usr/bin/bash
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /scripts/monitor/prometheus/start_test.sh                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 05:31:30 pm                                                   #
# Modified   : Friday August 16th 2024 09:35:18 pm                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
# Prometheus binary
PROMETHEUS_INSTALL_PATH="/usr/local/bin/prometheus"
# Test Config File
PROMETHEUS_CONFIG_FILE="config/prometheus_test.yaml"
# Start Prometheus with the custom configuration file
$PROMETHEUS_INSTALL_PATH --config.file=$PROMETHEUS_CONFIG_FILE --web.enable-admin-api
