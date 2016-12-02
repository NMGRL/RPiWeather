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

import time

import requests
import yaml

from config import Config


def bootstrap():
    from sense_hat import SenseHat

    dev = SenseHat()

    cfg = get_configuration()
    start_service(dev, cfg)


def get_configuration():
    d = os.path.join(os.path.expanduser('~'), '.weather')
    if not os.path.isdir(d):
        os.mkdir(d)

    cfg = {}
    p = os.path.join(d, 'config.yml')
    if os.path.isfile(p):
        with open(p,'r') as rfile:
            cfg = yaml.load(rfile)

    cfg = Config(**cfg)
    return cfg


def start_service(dev, cfg):
    period = cfg.period
    while 1:
        ctx = assemble_ctx(dev)
        post_event(dev, cfg, ctx)
        time.sleep(period)


PREV={}
def post_event(dev, cfg, ctx):
    if cfg.labspy_enabled:
        print 'posting'
        #requests.post(cfg.labspy_api_url, ctx)
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth(cfg.labspy_username, cfg.labspy_password)
        
   	for k,v in ctx.iteritems():
            process_id = cfg.get('labspy_{}_id'.format(k))
            if process_id is None:
                print 'process_id not available for {}'.format(k)
                continue
            prev = PREV.get(k)
            if prev is not None and abs(prev-v)<0.5:
                 print 'Not posting. current ={} previous={}'.format(v, prev)
                 continue
            PREV[k]=v
            url = '{}/measurements/'.format(cfg.labspy_api_url)
            #process_id = '{}/processinfos/{}'.format(cfg.labspy_api_url, process_id)
            payload = {'value':v, 'process_info': process_id}
        
            resp = requests.post(url, json=payload, auth=auth)
            if resp.status_code!=201:
                print 'url={}'.format(url)
                print 'payload={}'.format(payload)
                print 'response {} device_id={} k={} v={}'.format(resp, process_id, k, v)
                if resp.status_code==403:
                    print 'username={}, password={}'.format(cfg.labspy_username, cfg.labspy_password)
		elif resp.status_code in (500, 400):
                    for line in resp.iter_lines():
                        print line
                        raw_input()
                    import sys; sys.exit()
                    break
    if cfg.led_enabled:
        msg = 'Hum: {humidity:0.2f} Th: {tempH:0.2f} Tp: {tempP:0.2f} Atm: {atm_pressure:0.2f}'.format(**ctx)
        dev.show_message(msg, cfg.led_scroll_speed)

    if cfg.console_enabled:
        msg = ' '.join(['{}:{:0.2f}'.format(k, v) for k, v in ctx.iteritems()])
        print '{} {}'.format(time.time(), msg)

def assemble_ctx(dev):
    h = dev.get_humidity()
    th = dev.get_temperature_from_humidity()
    tp = dev.get_temperature_from_pressure()
    p = dev.get_pressure()
    return {'humidity': h, 'tempH': th, 'tempP': tp, 'atm_pressure': p}


if __name__ == '__main__':
    bootstrap()

# ============= EOF =============================================
