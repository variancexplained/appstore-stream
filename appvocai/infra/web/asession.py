#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/web/asession.py                                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:42:55 am                                                   #
# Modified   : Tuesday August 27th 2024 06:26:13 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
# import asyncio
# import logging
# import os
# import time
# from abc import ABC, abstractmethod
# from typing import Any, Dict, Optional

# import aiohttp
# from appvocai.domain.request.base import Request
# from appvocai.infra.base.config import Config
# from appvocai.infra.base.service import InfraService
# from appvocai.infra.web.adapter import Adapter
# from appvocai.infra.web.profile import SessionHistory, SessionProfile

# # ------------------------------------------------------------------------------------------------ #
# CUSTOM_CLIENT_ERROR_RETURN_CODE = 400
# CUSTOM_EXCEPTION_RETURN_CODE = 499


# # ------------------------------------------------------------------------------------------------ #
# #                                         ASESSION                                                 #
# # ------------------------------------------------------------------------------------------------ #
# class ASession(InfraService):
#     """Base class for asynchronous HTTP sessions and requests

#     Args:
#         throttle (AThrottle): Throttling mechanism to control request rate.
#         max_concurrency (int): Maximum number of concurrent requests.
#         retries (int): Number of retries if a request fails.
#         timeout (int): Timeout for requests in seconds.
#         config_cls (type[Config]): Class containing proxy server configurations.
#     """

#     def __init__(
#         self,
#         adapter: Adapter,
#         history: SessionHistory,
#         retries: int = 3,
#         timeout: int = 30,
#         concurrency: int = 50,
#         config_cls: type[Config] = Config,
#     ) -> None:
#         self._adapter = adapter
#         self._history = history
#         self._retries = retries
#         self._timeout = timeout
#         self._timeout_obj = aiohttp.ClientTimeout(total=timeout)
#         self._concurrency = concurrency
#         self._config = config_cls()

#         self._proxy = self._config.proxy

#         self._logger = logging.getLogger(f"{self.__class__.__name__}")

#     async def get(self, request: Request) -> Request:
#         """Formats and executes asynchronous get commands.

#         Args:
#             request (AsyncRequest): An Asyncronous HTTP Request
#         """
#         connector = aiohttp.TCPConnector()

#         concurrency = asyncio.Semaphore(self._concurrency)

#         # Create and start (send) profile object.
#         profile = SessionProfile()
#         profile.send()
#         # Get response using method defined in subclass.
#         response = await self.get_response(
#             request=request,
#             connector=connector,
#             timeout=self._timeout_obj,
#             profile=profile,
#             concurrency=concurrency,
#             trust_env=True,
#             raise_for_status=True,
#         )
#         # Computes average, total latency and response_time
#         profile.recv()
#         # Add the profile to the history object
#         self._history.add_profile(profile=profile)
#         # Engage the adapter.
#         self._adapter.adapt_requests(history=self._history)
#         # Obtain delay and concurrency
#         delay = self._adapter.session_control.delay
#         self._concurrency = int(self._adapter.session_control.concurrency)
#         # Execute the wait.
#         await asyncio.sleep(delay)
#         # Return results
#         return response

#     @abstractmethod
#     async def get_response(
#         self,
#         request: Request,
#         connector: aiohttp.TCPConnector,
#         timeout: aiohttp.ClientTimeout,
#         profile: SessionProfile,
#         concurrency: asyncio.Semaphore,
#         trust_env: bool = True,
#         raise_for_status: bool = True,
#     ) -> AsyncResponse:
#         """Formats and executes asynchronous get commands.

#         Args:
#             request (Request): An Asyncronous HTTP Request
#         """

#     async def make_request(
#         self,
#         client: aiohttp.ClientSession,
#         url: str,
#         concurrency: asyncio.Semaphore,
#         profile: SessionProfile,
#         params: Optional[Dict[str, object]] = None,
#     ) -> Optional[Dict[str, Any]]:
#         """Executes the HTTP request and returns a JSON response.

#         Args:
#             client (aiohttp.ClientSession): The HTTP client executing the request.
#             url (str): The base URL for the HTTP request.
#             concurrency (asyncio.Semaphore): Controls the number of concurrent requests.
#             params (Optional[Dict]): URL parameters. Optional.

#         Returns:
#             Optional[Dict[str, Any]]: The JSON response or None if all retries fail.
#         """
#         profile.requests += 1

#         async with concurrency:
#             while profile.retries < self._retries:
#                 try:
#                     start_time = time.time()
#                     async with client.get(
#                         url, proxy=self._proxy, ssl=False, params=params
#                     ) as response:
#                         response.raise_for_status()
#                         latency = time.time() - start_time
#                         profile.add_latency(latency=latency)
#                         profile.responses += 1
#                         result: Dict[str, Any] = await response.json(encoding="UTF-8")
#                         return result  # Only return after a successful request

#                 except aiohttp.ClientResponseError as e:
#                     if profile.retries == self._retries - 1:
#                         profile.log_error(return_code=e.status)
#                     if 400 <= e.status < 500:
#                         self._logger.warning(
#                             f"ClientResponseError: Response code: {e.status} - {e}. Retry #{profile.retries}."
#                         )

#                     elif 500 <= e.status < 600:
#                         self._logger.warning(
#                             f"ServerResponseError: Response code: {e.status} - {e}. Retry #{profile.retries}."
#                         )
#                     else:
#                         self._logger.warning(
#                             f"UnexpectedResponseError: Response code: {e.status} - {e}. Retry #{profile.retries}."
#                         )

#                 except aiohttp.ClientError as e:
#                     profile.log_error(return_code=CUSTOM_CLIENT_ERROR_RETURN_CODE)
#                     self._logger.warning(f"ClientError: {e}. Retry #{profile.retries}.")

#                 except Exception as e:
#                     profile.log_error(return_code=CUSTOM_EXCEPTION_RETURN_CODE)
#                     self._logger.warning(
#                         f"Unknown Error: {e}. Retry #{profile.retries}."
#                     )

#                 finally:
#                     profile.retries += 1
#                     await asyncio.sleep(2**profile.retries)  # Exponential backoff

#             # If all retries are exhausted, log and return None
#             self._logger.error("Exhausted retries. Returning to calling environment.")
#             return None


# # ------------------------------------------------------------------------------------------------ #
# #                                      ASESSION APPDATA                                            #
# # ------------------------------------------------------------------------------------------------ #
# class ASessionAppData(ASession):
#     """Asynchronous Session Handling and HTTP Request for App Data

#     Args:
#         url (str): The base url
#         param_list (list): List of parameter dictionaries.
#         headers (dict): Header dictionary. Optional
#     """

#     def __init__(
#         self,
#         adapter: Adapter,
#         history: SessionHistory,
#         retries: int = 3,
#         timeout: int = 30,
#         concurrency: int = 50,
#     ) -> None:
#         super().__init__(
#             adapter=adapter,
#             history=history,
#             retries=retries,
#             timeout=timeout,
#             concurrency=concurrency,
#         )

#     async def get_response(
#         self,
#         request: AppDataRequest,  # type: ignore
#         connector: aiohttp.TCPConnector,
#         timeout: aiohttp.ClientTimeout,
#         profile: SessionProfile,
#         concurrency: asyncio.Semaphore,
#         trust_env: bool = True,
#         raise_for_status: bool = True,
#     ) -> ResponseAppData:
#         """Formats and executes asynchronous get commands.

#         Args:
#             request (AsyncRequest): An Asyncronous HTTP Request
#         """

#         async with aiohttp.ClientSession(
#             headers=request.header,
#             connector=connector,
#             trust_env=trust_env,
#             raise_for_status=raise_for_status,
#             timeout=timeout,
#         ) as client:

#             tasks = [
#                 self.make_request(
#                     client=client,
#                     url=request.baseurl,
#                     concurrency=concurrency,
#                     profile=profile,
#                     params=param_dict,
#                 )
#                 for param_dict in request.param_list
#             ]
#             result = await asyncio.gather(*tasks)
#             return ResponseAppData(results=result, profile=profile)


# ------------------------------------------------------------------------------------------------ #
#                                      ASESSION REVIEW                                             #
# ------------------------------------------------------------------------------------------------ #
# class ASessionReview(ASession):

#     def __init__(
#         self,
#         adapter: Adapter,
#         history: SessionHistory,
#         retries: int = 3,
#         timeout: int = 30,
#         concurrency: int = 50,
#     ) -> None:
#         super().__init__(
#             adapter=adapter,
#             history=history,
#             retries=retries,
#             timeout=timeout,
#             concurrency=concurrency,
#         )

#     async def get_response(
#         self,
#         request: AsyncRequest,
#         connector: aiohttp.TCPConnector,
#         timeout: aiohttp.ClientTimeout,
#         profile: SessionProfile,
#         concurrency: asyncio.Semaphore,
#         trust_env: bool = True,
#         raise_for_status: bool = True,
#     ) -> ReviewAsyncResponse:
#         """Formats and executes asyncronous get commands.

#         Args:
#             request (AsyncRequest): An Asyncronous HTTP Request
#         """

#         async with aiohttp.ClientSession(
#             headers=request.header,
#             connector=connector,
#             trust_env=trust_env,
#             raise_for_status=raise_for_status,
#             timeout=timeout,
#         ) as client:
#             tasks = [
#                 self.make_request(
#                     client=client,
#                     url=url,
#                     concurrency=concurrency,
#                     profile=profile,
#                 )
#                 for url in request.urls
#             ]
#             return await asyncio.gather(*tasks)
