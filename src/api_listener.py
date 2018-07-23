#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. Created on 2018-07-15
.. codeauthor:: David Benes <benys94@gmail.com>
"""

import simplejson
import sys
from flask import Flask
from flask_restful import reqparse
from os.path import join, abspath, dirname, pardir
from werkzeug.exceptions import BadRequest

sys.path.append(join(abspath(dirname(__file__)), pardir))

from src.currency_core import (
    APIRequestError,
    CurrencyConversionError,
    CurrencyConverter,
    output_formatter
)

flask_app = Flask(__name__)
convert_core = None


def parse_request_arguments():
    """
    Parse arguments from HTTP request

    :return: Parsed arguments in dict
    :rtype: dict
    """
    parser = reqparse.RequestParser(bundle_errors=True)

    parser.add_argument(
        "amount", type=float, help="{error_msg}",
        required=True, location="args", dest="currency_amount"
    )

    parser.add_argument(
        "input_currency", type=str, help="Base currency for conversion",
        required=True, location="args"
    )

    parser.add_argument(
        "output_currency", type=str, help="Currency to be converted to",
        location="args", default=None
    )

    parsed_args = parser.parse_args()
    return parsed_args


@flask_app.route("/currency_converter")
def api_converter():
    """
    Handler for conversion API request

    :return: Text of response
    :rtype: str
    """
    try:
        parsed_args = parse_request_arguments()
        conversion_result = convert_core.convert_currency(**parsed_args)
    except (APIRequestError, CurrencyConversionError) as exc_msg:
        print(exc_msg)
        return simplejson.dumps({"error": str(exc_msg)}) + "\n"
    except BadRequest:
        return simplejson.dumps({"error": "Invalid request arguments"}) + "\n"
    else:
        return output_formatter(
            conversion_result, parsed_args["currency_amount"]
        ) + "\n"


if __name__ == '__main__':
    try:
        converter = CurrencyConverter()
    except CurrencyConversionError as e:
        print(e, file=sys.stderr)
    else:
        convert_core = converter
        flask_app.run()
