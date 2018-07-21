#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. Created on 2018-07-15
.. codeauthor:: David Benes <benys94@gmail.com>
"""

import requests
import simplejson
import sys
from os.path import join, abspath, dirname, pardir
from requests.exceptions import RequestException
from simplejson.errors import JSONDecodeError

sys.path.append(join(abspath(dirname(__file__)), pardir))

from src.common_utils import load_json_file


class APIRequestError(Exception):
    """
    Exception for handling error during HTTP requests
    """


class CurrencyConversionError(Exception):
    """
    Exception raised when currency given by user is invalid
    """


class CurrencyConverter:
    """
    Class for currency conversion.
    It handles all kind of currency operations.
    """
    CURRENCIES_FILE = join(
        abspath(dirname(__file__)), pardir, "data", "currencies.json"
    )

    def __init__(self, currencies_json=None):
        self._rates_api_address = "https://ratesapi.io/api/latest"

        # Set path to .json file with currencies and their symbols
        json_filepath = self.CURRENCIES_FILE
        if currencies_json is not None:
            json_filepath = currencies_json

        # Load data from file that contains JSON with all supported
        # currencies and their symbols
        try:
            currencies_data = load_json_file(filepath=json_filepath)
        except FileNotFoundError:
            raise CurrencyConversionError(
                "File '%s' with currency symbols doesn't exist" % json_filepath
            )
        except JSONDecodeError:
            raise CurrencyConversionError(
                "Invalid JSON in file '%s'" % json_filepath
            )
        else:
            self._mapped_currencies = map_symbols_to_currencies(
                currencies_data
            )

        # Try to get currency for given symbol. If symbol isn't found
        # given value itself is returned as currency
        self.symbol_to_currency = lambda x: self._mapped_currencies.get(x, x)

    def send_api_request(self, payload=None):
        """
        Get data from currency API service.
        API returns data in JSON but we may never know what could be wrong
        so string is also acceptable.

        :param dict payload:
            Parameters to be included into HTTP request
        :return: Response data
        :rtype: dict|str

        :raises APIRequestError:
            If there's any problem with API response
        """
        try:
            api_response = requests.get(
                self._rates_api_address,
                params=payload
            )
        except RequestException:
            raise APIRequestError(
                "Communication with ratesapi.io service has failed"
            )

        # Decode response and check for errors
        response_data = decode_response_message(api_response)
        if not isinstance(response_data, dict):
            raise APIRequestError(response_data)

        return response_data

    def convert_currency(
        self, currency_amount, input_currency, output_currency
    ):
        """
        Convert amount of currency according to passed arguments.

        :param float currency_amount:
            Amount of currency to be converted
        :param str input_currency:
            Type of input currency (e.g. 'USD', 'EUR', '$', ...)
        :param str output_currency:
            Type of output currency (e.g. 'USD', 'EUR', '$', ...)

        :return:
            Tuple with base currency and dictionary with conversion results
        :rtype: tuple(str, dict)
        """
        req_payload = {
            "base": self.symbol_to_currency(input_currency)
        }

        if output_currency is not None:
            req_payload["symbols"] = self.symbol_to_currency(output_currency)

        currency_rates = self.send_api_request(req_payload)
        if "error" in currency_rates:
            raise CurrencyConversionError(currency_rates["error"])
        elif not currency_rates["rates"]:
            raise CurrencyConversionError("Invalid output currency")

        convert_results = count_currency_amounts(
            currency_amount, currency_rates["rates"]
        )
        return req_payload["base"], convert_results


def count_currency_amounts(amount, currency_rates):
    """
    Count results for all possible rates according to base currency.

    :param float amount:
        Amount of currency to be converted
    :param dict currency_rates:
        Dictionary with currency rates
        {"<currency>": <rate>, ...}
    :return:
        Dictionary with all output currencies and computed values
    :rtype: dict{'EUR': 34.55, 'USD': 45.28, ...}
    """
    convert_results = {}
    for currency, rate in currency_rates.items():
        convert_results[currency] = round(rate * amount, 2)
    return convert_results


def map_symbols_to_currencies(currencies):
    """
    Create dictionary where key is symbol of currency and value is
    currency itself

    :param list currencies:
        List of dictionaries with data about many currencies
    :return: Dictionary with symbols and currencies
    :rtype: dict

    :raises KeyError: When given argument has wrong format
    """
    result_dict = {}
    for currency_dict in currencies:
        result_dict[currency_dict["symbol"]] = currency_dict["cc"]
    return result_dict


def decode_response_message(api_response):
    """
    Decode message received from API.
    Message should be in JSON format but there may be any problem
    that will return only plain text response (e.g. 404 error).

    :param requests.model.Response api_response:
        Unsuccessful response from currency service API
    :return:
        Dictionary with decoded JSON.
        If JSON couldn't be decoded plain text response is returned.
    :rtype: dict|str
    """
    try:
        response_msg = api_response.json()
    except JSONDecodeError:
        return api_response.text
    else:
        return response_msg


def output_formatter(conversion_results, amount):
    """
    Build output dictionary from computed data.

    :param tuple conversion_results:
        Tuple with  base currency and dictionary
        with conversion results.
    :param float amount:
        Amount of currency to convert
    :return: Output string
    :rtype: str
    """
    base_currency, conversions = conversion_results
    output_d = {
        "input": {
            "amount": amount,
            "currency": base_currency
        },
        "output": conversions
    }
    return simplejson.dumps(output_d, indent=4)
