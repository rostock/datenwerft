from django.http import JsonResponse
from django.template.loader import render_to_string
from jsonview.views import JsonView

from d3.models import VorgangMetadaten, Metadaten


class FetchMetaDataRequestView(JsonView):

    def get(self, request, *args, **kwargs):
        """
        Returns metadata for the given process ID as JSON.
        """
        process_id = request.GET.get('processId')

        if not process_id:
            return JsonResponse(
                {"error": "Missing 'processId' parameter."},
                status=400
            )

        process_metadata = VorgangMetadaten.objects.filter(vorgang__id=process_id)

        process_metadata_ids = process_metadata.values_list('id', flat=True)
        metadata = Metadaten.objects.filter(id__in=process_metadata_ids)

        html = render_to_string('d3/metadata_detail.html', {
            "metadata": [
                     {
                        "titel": meta.titel,
                        "wert": pm.wert
                     }
                     for pm in process_metadata
                     for meta in metadata
                     if pm.metadaten_id == meta.id
                 ]
        })

        return JsonResponse({"html": html})