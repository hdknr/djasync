# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from pycommand.djcommand import Command, SubCommand

import logging

log = logging.getLogger('djasync')


class Command(Command):

    class DumpDatabase(SubCommand):
        name = "dumpdb"
        description = _("Dump Celery Persistent Database File")
        args = [
            (('path',), dict(nargs=1, help="Celery Persistent File Path")),
        ]

        def run(self, params, **options):
            from djasync.utils import get_db_dict
            print get_db_dict(params.path[0])
