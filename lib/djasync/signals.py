from django.contrib.contenttypes.models import ContentType
# from django.db.models import signals
from celery import shared_task
from functools import wraps
import pydoc


@shared_task
def method_delegate(
        modname, funcname, instance_id=None, sender=None,
        *args, **kwargs):
    '''Delegator call signal recevier

    :param dict sender:  {'app_label': 'your_app_label','model': 'your_model'}
    '''
    if sender and instance_id and modname:
        instance = ContentType.objects.get(
            **sender).get_object_for_this_type(id=instance_id)
        if hasattr(instance, funcname):
            # TODO: there could be better way to identify method or function
            getattr(instance, funcname)(delayed=True,
                                        *args, **kwargs)
        else:
            mod = pydoc.locate(modname)
            getattr(mod, funcname)(instance=instance, delayed=True,
                                   *args, **kwargs)


def async_receiver(*args, **kwargs):
    ''' decorator for function for signal receiver '''
    def _decorator(decorated, *wargs, **wkwargs):

        @wraps(decorated)
        def _wrapped(instance,
                     delayed=False, signal=None, sender=None,
                     *dargs, **dkwargs):
            '''
            :param Model instance: Django Model instance
            :param Model sender: Django Model class
            '''
            if delayed:
                # 1st argument of function MUST be `instance`
                return decorated(instance,
                                 *dargs, **dkwargs)
            else:
                # drop `signal` argument
                if sender:
                    ct = ContentType.objects.get_for_model(sender)
                    sender = dict(app_label=ct.app_label, model=ct.model)

                method_delegate.delay(
                    decorated.__module__, decorated.func_name,
                    instance_id=instance.id, sender=sender,
                    *dargs, **dkwargs)

        return _wrapped

    return _decorator
