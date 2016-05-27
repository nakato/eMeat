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

from sqlalchemy import *  # noqa
from sqlalchemy.ext.declarative import declarative_base

from emeat import conf

DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata


def db_connect():
    return create_engine(conf['database'])


class attendees(DeclarativeBase):
    __tablename__ = "attendees"

    id = Column(Integer, primary_key=True)
    name = Column('name', Unicode)
    additional = Column('additional', Integer)

    def to_dict(self):
        return {
            'name': self.name,
            'additional': self.additional,
        }


class description(DeclarativeBase):
    __tablename__ = "description"

    id = Column(Integer, primary_key=True)
    title = Column('title', Unicode)
    description = Column('description', Unicode)

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
        }
