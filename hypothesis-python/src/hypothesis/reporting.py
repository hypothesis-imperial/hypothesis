# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis-python
#
# Most of this work is copyright (C) 2013-2018 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

import inspect

from hypothesis._settings import Verbosity, settings
from hypothesis.internal.compat import binary_type, print_unicode, \
    escape_unicode_characters
from hypothesis.utils.dynamicvariables import DynamicVariable

import os
import json


def silent(value):
    pass


def default(value):
    try:
        print_unicode(value)
    except UnicodeEncodeError:
        print_unicode(escape_unicode_characters(value))


reporter = DynamicVariable(default)
store = {'note': []}


def add_one_error(error):
    if 'errors' in store:
        store['errors'].append(error)
    else:
        store['errors'] = [error]


def update_error_store(key, value):
    if key == 'note':
        store[key].append(value)
    else:
        store[key] = value


def clean_error_store():
    store['note'] = []
    if 'errors' in store:
        del store['errors']
    if 'test_name' in store:
        del store['test_name']
    if 'statistics' in store:
        del store['statistics']


def get_error_store():
    return store


def write_error_store_to_file(fname):
    output = get_error_store()
    if not os.path.exists(fname):
        with open(fname, 'w') as f:
            outputs = {}
            outputs["pass"] = []
            outputs["fail"] = []
            json.dump(outputs, f, indent=4)
    with open(fname, 'r+') as f:
        outputs = json.loads(f.read())
        f.seek(0)
        if "errors" in output:
            outputs["fail"].append(output)
        else:
            outputs["pass"].append(output)
        json.dump(outputs, f, indent=4)
        f.truncate()


def delete_file(fname):
    if os.path.exists(fname):
        os.remove(fname)


def current_reporter():
    return reporter.value


def with_reporter(new_reporter):
    return reporter.with_value(new_reporter)


def current_verbosity():
    return settings.default.verbosity


def to_text(textish):
    if inspect.isfunction(textish):
        textish = textish()
    if isinstance(textish, binary_type):
        textish = textish.decode('utf-8')
    return textish


def verbose_report(text):
    if current_verbosity() >= Verbosity.verbose:
        current_reporter()(to_text(text))


def debug_report(text):
    if current_verbosity() >= Verbosity.debug:
        current_reporter()(to_text(text))


def report(text):
    if current_verbosity() >= Verbosity.normal:
        current_reporter()(to_text(text))
