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

from emeat.db import models
from sqlalchemy.orm import sessionmaker


class Event(object):

    def __init__(self):
        engine = models.db_connect()
        self.Session = sessionmaker(bind=engine, autocommit=True)

    def add_attendee(self, attendee, adds):
        session = self.Session()
        obj = {'name': attendee, 'additional': adds}
        attn = models.attendees(**obj)
        with session.begin():
            session.add(attn)
        session.close()

    def get_attendees(self):
        session = self.Session()
        attendees = {}
        for row in session.query(models.attendees).all():
            attendee = row.to_dict()
            name = attendee['name']
            attendees[name] = attendee['additional']
        return attendees

    def get_description(self):
        session = self.Session()
        description = session.query(models.description).first()
        if not description:
            return None
        return description.to_dict()

    def set_description(self, title, description):
        session = self.Session()
        obj = {'title': title, 'description': description}
        desc = models.description(**obj)
        with session.begin():
            session.add(desc)
        session.close()
