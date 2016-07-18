# Copyright 2016
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

import collections
import json
import os
import sys


class config(collections.Mapping):

    def _read_config(self):
        paths = [
            "%s/emeat.json" % os.getcwd(),
            os.path.expanduser("~/.emeat/emeat.json"),
            "/etc/emeat/emeat.json",
        ]

        # Todo, overlay configs.  Directory > Home > Sys
        for path in paths:
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    _config_json = f.read()
                break
        return _config_json

    def __init__(self):
        self._config = json.loads(self._read_config())

    def __getitem__(self, key):
        return self._config[key]

    def __len__(self):
        return len(self._config)

    def __iter__(self):
        return iter(self._config)


sys.modules[__name__] = config()
