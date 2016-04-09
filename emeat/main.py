import json
import logging
import sqlite3
from wsgiref import simple_server

import falcon


class StorageEngineSQ(object):

    def __init__(self, path):
        self._conn = sqlite3.connect(path)
        self._cur = self._conn.cursor()
        try:
            self._cur.execute(
                "CREATE TABLE attendees (name text, additional integer)")
            self._cur.execute(
                "CREATE TABLE description (title text, description text)")
            self._conn.commit()
        except Exception:
            pass

    def add_attendee(self, name, additional):
        if isinstance(name, str) and isinstance(additional, int):
            try:
                self._cur.execute(
                    "INSERT INTO attendees (name, additional) VALUES (?, ?);",
                    (name, additional))
                self._conn.commit()
            except Exception as e:
                raise StorageError(e)
        else:
            raise ValueError

    def get_attendees(self):
        for row in self._cur.execute("SELECT * FROM attendees ORDER BY name"):
            yield (row[0], row[1])

    def set_description(self, title, data):
        try:
            self._cur.execute(
                "INSERT INTO description (title, description) VALUES (?, ?);",
                (title, data))
            self._conn.commit()
        except Exception as e:
            raise StorageError(e)

    def get_description(self):
        for row in self._cur.execute("SELECT * FROM description"):
            return (row[0], row[1])


class StorageError(Exception):

    @staticmethod
    def handle(ex, req, resp, params):
        description = ('Sorry, couldn\'t write your thing to the '
                       'database. It worked on my box.')

        raise falcon.HTTPError(falcon.HTTP_725,
                               'Database Error',
                               description)


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
            # Nothing to do
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


class DatabaseMixin(object):

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger('eMeat.%s' % __name__)


class eMeat_GetAttendees(DatabaseMixin):

    def on_get(self, req, resp):
        attendees = {}
        for name, adds in self.db.get_attendees():
            attendees[name] = adds
        resp.body = json.dumps(attendees)


class eMeat_AddAttendee(DatabaseMixin):
    @falcon.before(max_body(10 * 1024))
    def on_post(self, req, resp):
        try:
            doc = req.context['doc']
        except Exception as ex:
            self.logger.error(ex)

            description = ('Aliens have attacked our base! We will '
                           'be back as soon as we fight them off. '
                           'We appreciate your patience.')

            raise falcon.HTTPServiceUnavailable(
                'Service Outage',
                description,
                30)

        resp.status = falcon.HTTP_200
        attendee = doc['attendee']
        additions = doc['additions']
        if isinstance(additions, str):
            additions = int(additions)
        db.add_attendee(attendee, additions)

        resp.status = falcon.HTTP_201


class eMeat_GetDescription(DatabaseMixin):
    def on_get(self, req, resp):
        title, description = self.db.get_description()
        attendees = {"title": title, "description": description}
        resp.body = json.dumps(attendees)


class eMeat_SetDescription(DatabaseMixin):
    @falcon.before(max_body(10 * 1024))
    def on_post(self, req, resp):
        try:
            doc = req.context['doc']
        except Exception as ex:
            self.logger.error(ex)

            description = ('Aliens have attacked our base! We will '
                           'be back as soon as we fight them off. '
                           'We appreciate your patience.')

            raise falcon.HTTPServiceUnavailable(
                'Service Outage',
                description,
                30)

        resp.status = falcon.HTTP_200
        title = doc['title']
        description = doc['data']
        db.set_description(title, description)

        resp.status = falcon.HTTP_201


app = falcon.API(middleware=[
    RequireJSON(),
    JSONTranslator(),
])

db = StorageEngineSQ('AusDayMeat.sqlite')
eMeatGet = eMeat_GetAttendees(db)
eMeatPut = eMeat_AddAttendee(db)
eMeatSetDesc = eMeat_SetDescription(db)
eMeatGetDesc = eMeat_GetDescription(db)
app.add_route('/get_attendees', eMeatGet)
app.add_route('/add_attendee', eMeatPut)
app.add_route('/set_description', eMeatSetDesc)
app.add_route('/get_description', eMeatGetDesc)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
