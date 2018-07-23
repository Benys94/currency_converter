#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. Created on 2018-07-22
.. codeauthor:: David Benes <benys94@gmail.com>
"""
import pytest

from simplejson.errors import JSONDecodeError
from tempfile import NamedTemporaryFile
from src.common_utils import load_json_file


@pytest.mark.parametrize(
    "test_data,expectation",
    (
        (
            '[{"a": 1}, {"b": 2}]',
            [{'a': 1}, {'b': 2}]
        ),
        (
            '{"a": 1, "b": 2}',
            {'a': 1, 'b': 2},
        ),
    )
)
def test_json_loader(test_data, expectation):
    """
    Test whether function for loading json files is working properly
    """
    with NamedTemporaryFile('w') as tmp_file:
        tmp_file.write(test_data)
        tmp_file.flush()

        result = load_json_file(tmp_file.name)

        assert result == expectation


@pytest.mark.parametrize(
    "test_data,no_temp, exception",
    (
        (
            'dummy content', False, JSONDecodeError
        ),
        (
            'dummy_filepath.json',
            True,
            FileNotFoundError,
        ),
    )
)
def test_json_loader_exceptions(test_data, no_temp, exception):
    """
    Test whether all method for loading .json files raises proper exceptions
    """
    with pytest.raises(exception):
        if no_temp:
            load_json_file(test_data)
        else:
            with NamedTemporaryFile('w') as tmp_file:
                tmp_file.write(test_data)
                tmp_file.flush()

                load_json_file(tmp_file.name)
