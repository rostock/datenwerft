import json

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import Subsets


class AddSubsetView(generic.View):
  """
  Add a new subset
  """
  http_method_names = ['post', ]

  def __init__(self):
    self.app_label = None
    self.model = None
    self.pk_field = None
    self.pks = None
    super().__init__()

  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    """
    ``dispatch()`` is called via ``AddSubsetView.as_view()`` in ``urls.py``;
    ``dispatch()`` forwards to ``post()`` since a **POST** request has been executed
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    print(request)
    self.app_label = request.POST.get('app_label', '')
    self.model = request.POST.get('model', '')
    self.pk_field = request.POST.get('pk_field', '')
    pks = request.POST.get('pks', '')
    print(self.app_label)
    print(self.model)
    print(self.pk_field)
    print(pks)
    self.pks = json.loads(pks)
    return super(AddSubsetView, self).dispatch(request, *args, **kwargs)

  @csrf_exempt
  def post(self, request, *args, **kwargs):
    """
    ``post()`` is called automatically by ``dispatch()``

    :param request:
    :param args:
    :param kwargs:
    :return: JSON response with ID of newly created subset or simple HTTP error response
    """
    try:
      content_type = ContentType.objects.filter(app_label=self.app_label, model=self.model)[0]
      subset = Subsets.objects.create(
        model=content_type,
        pk_field=self.pk_field,
        pks=self.pks
      )
      subset.save()
      response = {
          'id': str(subset.pk)
      }
      return JsonResponse(status=200, data=json.dumps(response), safe=False)
    except IntegrityError:
      return HttpResponse(status=500)
    except MultipleObjectsReturned:
      return HttpResponse(status=500)
    except Exception:
      raise Exception
