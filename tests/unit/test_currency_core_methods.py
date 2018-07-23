#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. Created on 2018-07-20
.. codeauthor:: David Benes <benys94@gmail.com>
"""

import pytest
import simplejson

from src.currency_core import (
    count_currency_amounts,
    decode_response_message,
    map_symbols_to_currencies,
    output_formatter
)


class DummyResponseClass:
    """
    Class to simulate API request response.
    """
    def __init__(self, response_content):
        self.text = response_content

    def json(self):
        """
        Convert text into dictionary if possible
        :return: Dictionary
        """
        return simplejson.loads(self.text)


@pytest.mark.parametrize(
    "dummy_response_obj,expectation",
    (
        (
            DummyResponseClass('{"a": 1, "b": 2}'),
            {"a": 1, "b": 2}
        ),
        (
            DummyResponseClass("Sample text response"),
            "Sample text response"
        )
    )
)
def test_response_decoder(dummy_response_obj, expectation):
    """
    Test method for decoding response messages from rest API
    """
    result = decode_response_message(dummy_response_obj)
    print(type(result))
    assert result == expectation


@pytest.mark.parametrize(
    "test_amount,test_rates, expectation",
    (
        (
            2.0,
            {"EUR": 1.5, "USD": 2.0},
            {"EUR": 3.00, "USD": 4.00}
        ),
        (
            54.67, {}, {}
        )
    )
)
def test_currency_counter(test_amount, test_rates, expectation):
    """
    Test whether currencies are counted properly
    """
    result = count_currency_amounts(test_amount, test_rates)
    assert result == expectation


@pytest.mark.parametrize(
    "test_data,expectation",
    (
        (
            [
                {"cc": "USD", "symbol": "$"},
                {"cc": "EUR", "symbol": "€"}
            ],
            {
                "$": "USD",
                "€": "EUR"
            }
        ),
        (
            [
                {"cc": "EUR", "foo": "blah"}
            ],
            KeyError
        ),
        (
            [
                {"foo": "blah", "symbol": "$"}
            ],
            KeyError
        ),
        (
            [
                {"dd": "EUR", "foo": "blah"}
            ],
            KeyError
        ),
        ([], {})
    )
)
def test_symbol_mapping(test_data, expectation):
    """
    Test whether function for mapping currencies to symbols
    works correctly
    """
    if not isinstance(expectation, dict):
        with pytest.raises(expectation):
            map_symbols_to_currencies(test_data)
    else:
        result = map_symbols_to_currencies(test_data)
        assert result == expectation


@pytest.mark.parametrize(
    "test_result,currency_amount,expect",
    (
        (
            ("EUR", {"USD": 44.44}), 22.22,
            simplejson.dumps({
                "input": {
                    "amount": 22.22,
                    "currency": "EUR"
                },
                "output": {
                    "USD": 44.44
                }
            }, indent=4)
        ),
    )
)
def test_output_formatter(test_result, currency_amount, expect):
    """
    Test whether output formatter return proper results
    """
    result = output_formatter(test_result, currency_amount)
    assert result == expect
