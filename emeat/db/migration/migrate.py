import os

from oslo_db.sqlalchemy import migration

from emeat import conf


class MigrationTool(object):

    def migrate_database(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'migration_repo')
        migration.db_sync(conf['database'], path)
