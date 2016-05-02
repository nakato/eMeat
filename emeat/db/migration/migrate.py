import os

from oslo_config import cfg
from oslo_db.sqlalchemy import migration

from emeat import conf

CONF = cfg.CONF


class MigrationTool(object):

    def migrate_database(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'migration_repo')
        migration.db_sync(CONF.database.uri, path)
