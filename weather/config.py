# ===============================================================================
# Copyright 2016 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
import os

import yaml


class Config:
    period = 1
    labspy_enabled = False
    labspy_api_url = ''

    led_enabled = True
    led_scroll_speed = 0.1

    console_enabled = True
    webserver_enabled = True

    def __init__(self, **kw):
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def get(self, k, default=None):
        ret = default
        if hasattr(self, k):
            ret = getattr(self, k)
        return ret


def get_configuration(name='config.yml'):
    d = os.path.join(os.path.expanduser('~'), '.weather')
    if not os.path.isdir(d):
        os.mkdir(d)

    cfg = {}
    p = os.path.join(d, name)
    if os.path.isfile(p):
        with open(p, 'r') as rfile:
            cfg = yaml.load(rfile)

    cfg = Config(**cfg)
    return cfg

# ============= EOF =============================================
