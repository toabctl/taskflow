# -*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys

from taskflow import decorators
from taskflow import test
from taskflow.utils import misc
from taskflow.utils import reflection


def mere_function(a, b):
    pass


def function_with_defs(a, b, optional=None):
    pass


def function_with_kwargs(a, b, **kwargs):
    pass


class Class(object):

    def method(self, c, d):
        pass

    @staticmethod
    def static_method(e, f):
        pass

    @classmethod
    def class_method(cls, g, h):
        pass


class CallableClass(object):
    def __call__(self, i, j):
        pass


class ClassWithInit(object):
    def __init__(self, k, l):
        pass


class GetCallableNameTest(test.TestCase):

    def test_mere_function(self):
        name = reflection.get_callable_name(mere_function)
        self.assertEquals(name, '.'.join((__name__, 'mere_function')))

    def test_method(self):
        name = reflection.get_callable_name(Class.method)
        self.assertEquals(name, '.'.join((__name__, 'Class', 'method')))

    def test_instance_method(self):
        name = reflection.get_callable_name(Class().method)
        self.assertEquals(name, '.'.join((__name__, 'Class', 'method')))

    def test_static_method(self):
        # NOTE(imelnikov): static method are just functions, class name
        #   is not recorded anywhere in them
        name = reflection.get_callable_name(Class.static_method)
        self.assertEquals(name, '.'.join((__name__, 'static_method')))

    def test_class_method(self):
        name = reflection.get_callable_name(Class.class_method)
        self.assertEquals(name, '.'.join((__name__, 'Class', 'class_method')))

    def test_constructor(self):
        name = reflection.get_callable_name(Class)
        self.assertEquals(name, '.'.join((__name__, 'Class')))

    def test_callable_class(self):
        name = reflection.get_callable_name(CallableClass())
        self.assertEquals(name, '.'.join((__name__, 'CallableClass')))

    def test_callable_class_call(self):
        name = reflection.get_callable_name(CallableClass().__call__)
        self.assertEquals(name, '.'.join((__name__, 'CallableClass',
                                          '__call__')))


class GetRequiredCallableArgsTest(test.TestCase):

    def test_mere_function(self):
        result = reflection.get_required_callable_args(mere_function)
        self.assertEquals(['a', 'b'], result)

    def test_function_with_defaults(self):
        result = reflection.get_required_callable_args(function_with_defs)
        self.assertEquals(['a', 'b'], result)

    def test_method(self):
        result = reflection.get_required_callable_args(Class.method)
        self.assertEquals(['self', 'c', 'd'], result)

    def test_instance_method(self):
        result = reflection.get_required_callable_args(Class().method)
        self.assertEquals(['c', 'd'], result)

    def test_class_method(self):
        result = reflection.get_required_callable_args(Class.class_method)
        self.assertEquals(['g', 'h'], result)

    def test_class_constructor(self):
        result = reflection.get_required_callable_args(ClassWithInit)
        self.assertEquals(['k', 'l'], result)

    def test_class_with_call(self):
        result = reflection.get_required_callable_args(CallableClass())
        self.assertEquals(['i', 'j'], result)

    def test_decorators_work(self):
        @decorators.locked
        def locked_fun(x, y):
            pass
        result = reflection.get_required_callable_args(locked_fun)
        self.assertEquals(['x', 'y'], result)


class AcceptsKwargsTest(test.TestCase):

    def test_no_kwargs(self):
        self.assertEquals(
            reflection.accepts_kwargs(mere_function), False)

    def test_with_kwargs(self):
        self.assertEquals(
            reflection.accepts_kwargs(function_with_kwargs), True)


class GetClassNameTest(test.TestCase):

    def test_std_class(self):
        name = reflection.get_class_name(RuntimeError)
        self.assertEquals(name, 'exceptions.RuntimeError')

    def test_class(self):
        name = reflection.get_class_name(Class)
        self.assertEquals(name, '.'.join((__name__, 'Class')))

    def test_instance(self):
        name = reflection.get_class_name(Class())
        self.assertEquals(name, '.'.join((__name__, 'Class')))

    def test_int(self):
        name = reflection.get_class_name(42)
        self.assertEquals(name, '__builtin__.int')


class GetAllClassNamesTest(test.TestCase):

    def test_std_class(self):
        names = list(reflection.get_all_class_names(RuntimeError))
        self.assertEquals(names, [
            'exceptions.RuntimeError',
            'exceptions.StandardError',
            'exceptions.Exception',
            'exceptions.BaseException',
            '__builtin__.object'])

    def test_std_class_up_to(self):
        names = list(reflection.get_all_class_names(RuntimeError,
                                                    up_to=Exception))
        self.assertEquals(names, [
            'exceptions.RuntimeError',
            'exceptions.StandardError',
            'exceptions.Exception'])


class ExcInfoUtilsTest(test.TestCase):

    def _make_ex_info(self):
        try:
            raise RuntimeError('Woot!')
        except Exception:
            return sys.exc_info()

    def test_copy_none(self):
        result = misc.copy_exc_info(None)
        self.assertIsNone(result)

    def test_copy_exc_info(self):
        exc_info = self._make_ex_info()
        result = misc.copy_exc_info(exc_info)
        self.assertIsNot(result, exc_info)
        self.assertIs(result[0], RuntimeError)
        self.assertIsNot(result[1], exc_info[1])
        self.assertIs(result[2], exc_info[2])

    def test_none_equals(self):
        self.assertTrue(misc.are_equal_exc_info_tuples(None, None))

    def test_none_ne_tuple(self):
        exc_info = self._make_ex_info()
        self.assertFalse(misc.are_equal_exc_info_tuples(None, exc_info))

    def test_tuple_nen_none(self):
        exc_info = self._make_ex_info()
        self.assertFalse(misc.are_equal_exc_info_tuples(exc_info, None))

    def test_tuple_equals_itself(self):
        exc_info = self._make_ex_info()
        self.assertTrue(misc.are_equal_exc_info_tuples(exc_info, exc_info))

    def test_typle_equals_copy(self):
        exc_info = self._make_ex_info()
        copied = misc.copy_exc_info(exc_info)
        self.assertTrue(misc.are_equal_exc_info_tuples(exc_info, copied))
