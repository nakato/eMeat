import os

from alembic.config import CommandLine
from alembic.config import Config

# Nasty hack because we use oslo.config
ARGV = os.sys.argv[1:]
os.sys.argv = os.sys.argv[0:1]

from emeat import conf
from oslo_config import cfg

CONF = cfg.CONF


def main():
    path = os.path.dirname(__file__)
    ini_path = os.path.join(path, 'alembic.ini')
    cl = CommandLine()
    opts = cl.parser.parse_args(ARGV)
    if not hasattr(opts, "cmd"):
        cl.parser.error("too few arguments")
    alembic_config = Config(ini_path, cmd_opts=opts)
    alembic_config.set_section_option(
        'alembic', 'sqlalchemy.url', CONF.database.uri)
    cl.run_cmd(alembic_config, opts)
