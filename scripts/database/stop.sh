#!/usr/bin/bash
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project  : DeepCTR: Deep Learning and Neural Architecture Selection for CTR Prediction     #
# Version  : 0.1.0                                                                                 #
# File     : /stop.sh                                                                              #
# Language : Python 3.7.12                                                                         #
# ------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                            #
# Email    : john@variancexplained.com                                                        #
# URL      : https://github.com/variancexplained/DeepCTR                                        #
# ------------------------------------------------------------------------------------------------ #
# Created  : Friday, April 15th 2022, 3:02:10 pm                                                   #
# Modified : Sunday, April 24th 2022, 4:24:53 pm                                                   #
# Modifier : John James (john@variancexplained.com)                                           #
# ------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                               #
# Copyright: (c) 2022 Bryant St. Labs                                                              #
# ================================================================================================ #
echo $'\nStopping MySQL...'
sudo /etc/init.d/mysql stop
