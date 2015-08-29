# -*- coding: utf-8 -*-
import types
import os
# import sys
from celery import Celery


class CeleryModule(types.ModuleType):
    ''' Celery
    '''
    def __init__(self, hosting_script, name="celery_loader", app='app',
                 *args, **kwargs):

        app_dir = os.path.dirname(os.path.abspath(hosting_script))
        self.main_app = os.path.basename(app_dir)
        self.project_dir = os.path.dirname(app_dir)
        self.settings_module = "{0}.settings".format(self.main_app)

        if 'DJANGO_SETTINGS_MODULE' not in os.environ:
            os.environ.setdefault(
                'DJANGO_SETTINGS_MODULE', self.settings_module)

        from django.conf import settings
        celery = Celery(name)
        celery.config_from_object('django.conf:settings')
        celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
        self.app = celery           # entry point

        super(CeleryModule, self).__init__(name, *args, **kwargs)
