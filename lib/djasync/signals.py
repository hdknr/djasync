from django.contrib.contenttypes.models import ContentType
from django.dispatch import dispatcher

from celery import shared_task
from functools import wraps

method_called = dispatcher.Signal(providing_args=["instance", "method", ])


def model_method_async(instance, action, *args, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    model_method.apply_async(
        args=(ct.id, instance.id, action, ) + args,
        kwargs=kwargs)


@shared_task
def model_method(content_type_id, id, action, *args, **kwargs):
    ct = ContentType.objects.get(id=content_type_id)
    obj = ct.get_object_for_this_type(id=id)
    return getattr(obj, action, lambda: '')(*args, **kwargs)


def async_call(signal=method_called, *args, **kwargs):
    ''' asynchronous method call '''

    def _decorator(method, *d_args, **d_kwargs):

        @wraps(method)
        def wrapped(self, delayed=False, *m_args, **m_kwargs):
            if delayed:
                model_method_async(
                    self, method.func_name, *m_args, **m_kwargs)
            else:
                if signal:
                    ct = ContentType.objects.get_for_model(self)
                    signal.send(
                        sender=ct.model_class(), instance=self,
                        method=method.func_name)
                return method(self, *m_args, **m_kwargs)
        return wrapped

    return _decorator
