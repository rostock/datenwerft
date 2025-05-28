from django.contrib import admin

from .models import (
  Codelist,
  CodelistValue,
)

@admin.register(Codelist)
class CodelistAdmin(admin.ModelAdmin):
  list_display = (
    'uuid',
    'modified',
    'name',
    'title',
  )
  search_fields = (
    'modified',
    'uuid',
    'name',
    'title',
  )


@admin.register(CodelistValue)
class CodelistValueAdmin(admin.ModelAdmin):
  list_display = (
    'uuid',
    'modified',
    'codelist',
    'value',
    'parent',
    'ordinal',
    'title',
    'description',
  )
  search_fields = (
    'modified',
    'uuid',
    'codelist__name',
    'codelist__title',
    'value',
    'ordinal',
    'title',
    'description',
  )
  empty_value_display = ''
