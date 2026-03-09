from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from jsonview.views import JsonView


class FetchModelDatabaseConfigRequestView(JsonView):
  def get(self, request, *args, **kwargs):
    """
    Liefert Metadaten von Models basieren des Model-Identifiers. Der Endpunkt ist auf
    Superuser beschränkt.

    Parameters:
        request (HttpRequest): HTTP Request der ausgewertet werden soll.
        *args: Zusätzliche Argumente, die an die Methode übergeben wurden.
        **kwargs: Zusätzliche Keyword-Argumente, die an die Methode übergeben wurden.

    Returns:
        JsonResponse: Response, welches die Metadaten des Models oder Fehlermeldungen beinhaltet

    Errors:
        403: Der Nutzer ist kein Superuser.
        400: Der Parameter "modelId" fehlt.
    """
    if not request.user.is_superuser:
      return JsonResponse({'error': 'Forbidden'}, status=403)

    model_id = request.GET.get('modelId')

    if not model_id:
      return JsonResponse({'error': "Missing 'modelId' parameter."}, status=400)

    content_type = ContentType.objects.get(id=model_id)

    try:
      model = apps.get_model(app_label=content_type.app_label, model_name=content_type.model)
      print(model.objects.model._meta.pk.name)
      db_table = model.objects.model._meta.db_table
      schema = db_table.split('"."')[0]
      table = db_table.split('"."')[1]
      id_field = model.objects.model._meta.pk.name
    except Exception:
      schema = None
      table = None
      id_field = None

    response = {
      'name': content_type.name.lower(),
      'title': content_type.name,
      'schema': schema,
      'table': table,
      'id_field': id_field,
    }

    return JsonResponse(response)
