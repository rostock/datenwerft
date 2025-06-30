from django.contrib.contenttypes.models import ContentType
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.urls import reverse

from d3.models import Vorgang
from d3.utils import fetch_processes


class TableProcessView(BaseDatatableView):
    """
    View to return JSON data for the Vorgang model.
    """

    def __init__(self, model=None, *args, **kwargs):
        self.model = Vorgang
        model_name = self.model.__name__
        model_name_lower = model_name.lower()
        self.model_name = model_name
        self.model_name_lower = model_name_lower

        if model is not None:
            self.datenmanagement_model_name = model.__name__
            self.datenmanagement_model_lower = self.datenmanagement_model_name.lower()
            self.content_type_id = ContentType.objects.get(
                app_label='datenmanagement',
                model=self.datenmanagement_model_lower
            ).id
        else:
            self.datenmanagement_model_name = ''
            self.datenmanagement_model_lower = ''
            self.content_type_id = None

        self.model_is_editable = self.model.BasemodelMeta.editable
        self.columns = list(self.model.BasemodelMeta.list_fields.keys())
        self.columns_with_date = self.model.BasemodelMeta.list_fields_with_date
        self.columns_with_datetime = self.model.BasemodelMeta.list_fields_with_datetime
        self.columns_with_decimal = self.model.BasemodelMeta.list_fields_with_decimal
        self.columns_with_foreign_key = self.model.BasemodelMeta.list_fields_with_foreign_key
        self.additional_foreign_key_column = self.model.BasemodelMeta.list_additional_foreign_key_field
        self.column_as_highlight_flag = self.model.BasemodelMeta.highlight_flag
        self.thumbs = self.model.BasemodelMeta.thumbs

        super().__init__(*args, **kwargs)

    def get_initial_queryset(self):

        qs = fetch_processes(self.content_type_id, self.kwargs.get('pk'))
        if qs is None:
            return Vorgang.objects.none()  # Avoid NoneType crash
        return qs

    def prepare_results(self, qs):
        results = []

        for obj in qs:
            row = []

            for field in self.columns:
                value = getattr(obj, field)
                if hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d %H:%M')
                elif value is None:
                    value = ''
                else:
                    value = str(value)
                row.append(value)

            results.append(row)

        return results



class D3ContextMixin:

    def get_d3_context(self, context, model, pk):

        self.model = model
        model_name = self.model.__name__

        context['column_titles'] = list(Vorgang.BasemodelMeta.list_fields.values())

        context['url_process_tabledata'] = reverse(
            'd3:' + model_name + '_fetch_process_list',
            kwargs={'pk': pk}
        )

        context['url_process_add']  = reverse('d3:' + model_name + '_d3_add_process', kwargs={'pk': pk})

        return context