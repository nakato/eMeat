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

import json
import logging

import falcon

from emeat.controllers import event


class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://json.org')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.',
                    href='json.org')


class JSONTranslator(object):

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            if req.method in ('POST', 'PUT'):
                raise falcon.HTTPBadRequest('A request body is required')
            else:
                return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'])


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

    def __init__(self):
        self.event = event.Event()
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
        RequireJSON(),
        JSONTranslator(),
    ])

    eMeatGet = eMeat_GetAttendees()
    eMeatPut = eMeat_AddAttendee()
    eMeatSetDesc = eMeat_SetDescription()
    eMeatGetDesc = eMeat_GetDescription()
    application.add_route('/get_attendees', eMeatGet)
    application.add_route('/add_attendee', eMeatPut)
    application.add_route('/set_description', eMeatSetDesc)
    application.add_route('/get_description', eMeatGetDesc)
    return application
