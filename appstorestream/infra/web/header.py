#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoC: AppStore Voice of the Customer                                              #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvoc/infrastructure/web/header.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvoc                                          #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:43:55 am                                                   #
# Modified   : Friday July 19th 2024 04:44:15 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Headers Module."""
from __future__ import annotations

import random

from appvoc.infrastructure.web.base import Header


# ------------------------------------------------------------------------------------------------ #
class BrowserHeader:
    """Iteratively and randomly returns HTTP Browser headers

    Args:
        headers (list): List of browser header dictionaries
    """

    def __init__(self) -> None:
        self._headers = HEADERS
        self._header = None

    def __iter__(self):
        """Initializes the iteration"""
        return self

    def __next__(self):
        """Returns a randomly selected header."""

        while True:
            header = random.choice(self._headers)
            if header != self._header:
                self._header = header
                return header


# ------------------------------------------------------------------------------------------------ #
class AppleStoreFrontHeader(Header):
    """Iteratively and randomly returns HTTP Browser headers

    Args:
        headers (list): List of browser header dictionaries
    """

    def __init__(self) -> None:
        self._headers = STOREFRONT

    def __iter__(self):
        """Initializes the iteration"""
        return self

    def __next__(self):
        """Returns an apple storefront header."""
        return self._headers


# ------------------------------------------------------------------------------------------------ #
#                               APPSTORE STOREFRONT HEADER                                         #
# ------------------------------------------------------------------------------------------------ #
STOREFRONT = {
    "country": "us",
    "headers": {"X-Apple-Store-Front": "143441-1,29"},
}


# ------------------------------------------------------------------------------------------------ #
#                                STANDARD BROWSER HEADERS                                          #
# ------------------------------------------------------------------------------------------------ #
HEADERS = [
    {
        "authority": "www.apple.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "cookie": "geo=US; s_fid=06052E4035BD477E-287EA4F0D67179DA; s_cc=true; mk_epub=%7B%22btuid%22%3A%221p309rf%22%2C%22prop57%22%3A%22www.us.itunes%22%7D; s_vi=[CS]v1|32164EB46DD3A424-60001FE203923437[CE]; pt-dm=v1~x~90ni8h34~m~1~n~itunes%20-%20index%20(us)",
        "pragma": "no-cache",
        "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    },
    {
        "authority": "www.apple.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "cookie": "geo=US; s_fid=06052E4035BD477E-287EA4F0D67179DA; s_cc=true; mk_epub=%7B%22btuid%22%3A%221p309rf%22%2C%22prop57%22%3A%22www.us.itunes%22%7D; s_vi=[CS]v1|32164EB46DD3A424-60001FE203923437[CE]; pt-dm=v1~x~90ni8h34~m~1~n~itunes%20-%20index%20(us)",
        "pragma": "no-cache",
        "sec-ch-ua": '"Google Chrome";v="110", "Not(A:Brand";v="8", "Chromium";v="110"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:111.0) Gecko/20100101 Firefox/111.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    },
    {
        "authority": "www.apple.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "geo=US; s_fid=30A04E3CF3D9F051-1CE913ACD3B58514; s_cc=true; mk_epub=%7B%22btuid%22%3A%2262q2jj%22%2C%22prop57%22%3A%22www.us.itunes%22%7D; s_vi=[CS]v1|321651851683436F-40001437604D6F47[CE]; pt-dm=v1~x~za8r1msw~m~1~n~itunes%20-%20index%20(us)",
        "sec-ch-ua": '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    },
    {
        "authority": "www.apple.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "geo=US; s_fid=30A04E3CF3D9F051-1CE913ACD3B58514; s_cc=true; mk_epub=%7B%22btuid%22%3A%2262q2jj%22%2C%22prop57%22%3A%22www.us.itunes%22%7D; s_vi=[CS]v1|321651851683436F-40001437604D6F47[CE]; pt-dm=v1~x~za8r1msw~m~1~n~itunes%20-%20index%20(us)",
        "sec-ch-ua": '"Microsoft Edge";v="110", "Not(A:Brand";v="8", "Chromium";v="110"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    },
    {
        "authority": "www.apple.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "geo=US; s_fid=037BA24B83F1E75D-00847AB1DC3C8B16; s_cc=true; mk_epub=%7B%22btuid%22%3A%22v2gsww%22%2C%22prop57%22%3A%22www.us.itunes%22%7D; pt-dm=v1~x~es8yixh8~m~1~n~itunes%20-%20index%20(us)",
        "sec-ch-ua": '"Not?A_Brand";v="99", "Opera";v="97", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0",
    },
]
