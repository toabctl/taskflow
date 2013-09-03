# -*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
#    Copyright (C) 2013 Rackspace Hosting All Rights Reserved.
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

from distutils import version


def get_task_version(task):
    """Gets a tasks *string* version, whether it is a task object/function."""
    task_version = getattr(task, 'version')
    if isinstance(task_version, (list, tuple)):
        task_version = '.'.join(str(item) for item in task_version)
    if task_version is not None and not isinstance(task_version, basestring):
        task_version = str(task_version)
    return task_version


def is_version_compatible(version_1, version_2):
    """Checks for major version compatibility of two *string" versions."""
    try:
        version_1_tmp = version.StrictVersion(version_1)
        version_2_tmp = version.StrictVersion(version_2)
    except ValueError:
        version_1_tmp = version.LooseVersion(version_1)
        version_2_tmp = version.LooseVersion(version_2)
    version_1 = version_1_tmp
    version_2 = version_2_tmp
    if version_1 == version_2 or version_1.version[0] == version_2.version[0]:
        return True
    return False


class LastFedIter(object):
    """An iterator which yields back the first item and then yields back
    results from the provided iterator.
    """

    def __init__(self, first, rest_itr):
        self.first = first
        self.rest_itr = rest_itr

    def __iter__(self):
        yield self.first
        for i in self.rest_itr:
            yield i