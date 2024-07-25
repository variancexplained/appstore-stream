#!/usr/bin/bash
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project  : DeepCTR: Deep Learning and Neural Architecture Selection for CTR Prediction     #
# Version  : 0.1.0                                                                                 #
# File     : /restart.sh                                                                           #
# Language : Python 3.7.12                                                                         #
# ------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                            #
# Email    : john@variancexplained.com                                                        #
# URL      : https://github.com/variancexplained/DeepCTR                                        #
# ------------------------------------------------------------------------------------------------ #
# Created  : Friday, April 15th 2022, 3:01:43 pm                                                   #
# Modified   : Tuesday April 18th 2023 07:58:15 am                                                 #
# Modifier : John James (john@variancexplained.com)                                           #
# ------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                               #
# Copyright: (c) 2022 Bryant St. Labs                                                              #
# ================================================================================================ #
echo $'\nRestart MySQL...'
sudo /etc/init.d/mysql restart
