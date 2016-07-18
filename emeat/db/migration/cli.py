import os

from alembic.config import CommandLine
from alembic.config import Config

from emeat import conf


def main(args=None):
    path = os.path.dirname(__file__)
    ini_path = os.path.join(path, 'alembic.ini')
    cl = CommandLine()
    if args:
        opts = cl.parser.parse_args(args)
    else:
        opts = cl.parser.parse_args()
    if not hasattr(opts, "cmd"):
        cl.parser.error("too few arguments")
    alembic_config = Config(ini_path, cmd_opts=opts)
    alembic_config.set_section_option(
        'alembic', 'sqlalchemy.url', conf['database'])
    cl.run_cmd(alembic_config, opts)
