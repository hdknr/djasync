# -*- coding: utf-8 -*-
import types
import os
import sys
from kombu import Exchange, Queue
from celery import Celery
from itertools import chain


class CeleryLoader(types.ModuleType):
    ''' Celery
    '''
    DEFAULT_JOBQ = 'sandbox'

    DEFAULT_CONF = CELERY = dict(
        CELERY_RESULT_BACKEND='amqp',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
        BROKER_URL='amqp://{JOBQ}:{JOBQ}@localhost:5672/{JOBQ}'.format(
            JOBQ=DEFAULT_JOBQ),
        CELERY_DEFAULT_QUEUE=DEFAULT_JOBQ,
        CELERY_QUEUES=(Queue(DEFAULT_JOBQ, Exchange(DEFAULT_JOBQ),
                       routing_key=DEFAULT_JOBQ),),
        # CELERY_ALWAYS_EAGER=True,
    )

    def __init__(self, hosting_script, name="celery_loader", *args, **kwargs):
        app_dir = os.path.dirname(os.path.abspath(hosting_script))
        self.main_app = os.path.basename(app_dir)
        self.project_dir = os.path.dirname(app_dir)
        self.settings_module = "{0}.settings".format(self.main_app)

        super(CeleryLoader, self).__init__(name, *args, **kwargs)

    @classmethod
    def create(cls, confs={}, name='app'):
        confs = dict(chain.from_iterable(d.iteritems()
                     for d in (cls.DEFAULT_CONF, confs)))
        from django.conf import settings
        celery = Celery('app')
        celery.config_from_object(confs)
        celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
        return celery

    @property
    def app(self):
        ''' Celery Runner Entry Point '''
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', self.settings_module)
        sys.path.insert(0, self.project_dir)

        from django import setup, apps
        setup()
        return apps.apps.get_app_config(self.main_app).celery
