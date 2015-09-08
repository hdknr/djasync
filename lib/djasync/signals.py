# from django.contrib.contenttypes.models import ContentType
# from django.db.models import signals
from celery import shared_task
from functools import wraps
import pydoc


@shared_task
def method_delegate(
        modname, funcname, instance_id=None, sender=None,
        *args, **kwargs):
    '''Delegator call signal recevier '''
    if sender and instance_id and modname:
        instance = sender.objects.get(id=instance_id)
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
    def _wrapper(decorated, *wargs, **wkwargs):

        def _decorator(instance,
                       delayed=False, signal=None, sender=None,
                       *dargs, **dkwargs):
            if delayed:
                # 1st argument of function MUST be `instance`
                return decorated(instance,
                                 *dargs, **dkwargs)
            else:
                # drop `signal` argument
                method_delegate.delay(
                    decorated.__module__, decorated.func_name,
                    instance_id=instance.id,
                    sender=sender or type(instance),
                    *dargs, **dkwargs)

        return wraps(decorated)(_decorator)

    return _wrapper
