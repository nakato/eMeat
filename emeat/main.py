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

import logging

import falcon

from emeat.controllers import event
from emeat.middleware import json


def max_body(limit):

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class ControllerMixin(object):

    def __init__(self, db_control):
        self.event = db_control
        self.logger = logging.getLogger('eMeat.%s' % __name__)


class eMeat_GetAttendees(ControllerMixin):

    def on_get(self, req, resp):
        req.context['result'] = self.event.get_attendees()


class eMeat_AddAttendee(ControllerMixin):
    @falcon.before(max_body(10 * 1024))
    def on_post(self, req, resp):
        doc = req.context['doc']
        attendee = doc['attendee']
        additions = doc['additions']
        if isinstance(additions, str):
            additions = int(additions)
        self.event.add_attendee(attendee, additions)
        resp.status = falcon.HTTP_201


class eMeat_GetDescription(ControllerMixin):
    def on_get(self, req, resp):
        req.context['result'] = self.event.get_description()


class eMeat_SetDescription(ControllerMixin):
    @falcon.before(max_body(10 * 1024))
    def on_post(self, req, resp):
        doc = req.context['doc']
        title = doc['title']
        description = doc['data']
        self.event.set_description(title, description)
        resp.status = falcon.HTTP_201


def main():
    application = falcon.API(middleware=[
        json.RequireJSON(),
        json.JSONTranslator(),
    ])

    db_control = event.Event()

    eMeatGet = eMeat_GetAttendees(db_control)
    eMeatPut = eMeat_AddAttendee(db_control)
    eMeatSetDesc = eMeat_SetDescription(db_control)
    eMeatGetDesc = eMeat_GetDescription(db_control)
    application.add_route('/get_attendees', eMeatGet)
    application.add_route('/add_attendee', eMeatPut)
    application.add_route('/set_description', eMeatSetDesc)
    application.add_route('/get_description', eMeatGetDesc)
    return application
