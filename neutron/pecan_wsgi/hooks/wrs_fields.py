# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Copyright (c) 2017-2018 Wind River Systems, Inc.
#

from neutron.common import constants as n_const
from pecan import hooks


class WrsFieldsHook(hooks.PecanHook):

    # Do this at around the same as body validation hook
    # we use this to strip out wrs- attributes when the request
    # comes from a non-wrs client
    # this is part of compliance to refstack, tempest, functest etc
    priority = 121

    def after(self, state):
        # filter out wrs fields when the request does not
        # comes from a wrs client
        if state.request.headers.get('wrs-header') is not None:
            return

        try:
            data = state.response.json
        except ValueError:
            return
        resource = state.request.context.get('resource')
        collection = state.request.context.get('collection')
        if collection not in data and resource not in data:
            return
        is_single = resource in data
        key = resource if resource in data else collection
        if is_single:
            data[key] = self._filter_item(
                state.response.json[key])
        else:
            data[key] = [
                self._filter_item(i)
                for i in state.response.json[key]
            ]
        state.response.json = data

    def _filter_item(self, item):
        return {
            field: value
            for field, value in item.items()
            if not field.startswith(n_const.WRS_FIELD_PREFIX)
        }
