#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. Created on 2018-07-14
.. codeauthor:: David Benes <benys94@gmail.com>
"""

import argparse
import sys
from os.path import join, abspath, dirname, pardir

sys.path.append(join(abspath(dirname(__file__)), pardir))

from src.currency_core import (
    APIRequestError,
    CurrencyConversionError,
    CurrencyConverter,
    output_formatter
)


def parse_args(cmd_args):
    """
    Parse command-line arguments

    :param list cmd_args: List of command-line arguments
    :return: Dictionary with parsed arguments
    :rtype: dict
    """

    parser = argparse.ArgumentParser(
        description="Command-line tool for currency conversion."
    )

    parser.add_argument(
        "--amount", dest="currency_amount", metavar="<float>", type=float,
        required=True, help="Amount of currency to be converted."
    )

    parser.add_argument(
        "--input_currency", dest="input_currency", metavar="<str>",
        required=True, type=str, help="Type of currency to be converted from."
    )

    parser.add_argument(
        "--output_currency", dest="output_currency", metavar="<str>",
        type=str, help="Type of currency to convert to.", default=None
    )

    parsed_args = parser.parse_args(cmd_args)
    return vars(parsed_args)


def run_conversion(**kwargs):
    """
    Run conversion process
    """
    ccs = CurrencyConverter()
    try:
        results = ccs.convert_currency(**kwargs)
    except (APIRequestError, CurrencyConversionError) as e:
        return "{'error': %s}" % e
    else:
        formatted_output = output_formatter(results, kwargs["currency_amount"])

    return formatted_output


if __name__ == '__main__':
    arguments = parse_args(sys.argv[1:])
    result = run_conversion(**arguments)
    print(result)
