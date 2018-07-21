#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. Created on 2018-07-15
.. codeauthor:: David Benes <benys94@gmail.com>
"""

import simplejson


def load_json_file(filepath):
    """
    Load content from .json file with given path

    :param filepath: Path to .json file
    :return:
        Content of .json file
        or empty dict when file's content couldn't be decoded
    """
    with open(filepath, 'r') as json_file:
        file_data = simplejson.load(json_file)
    return file_data
