from django.db.models import options

#
# custom meta attributes for models
#

options.DEFAULT_NAMES += (
  # optional | bool | is the model a codelist?
  'codelist',
  # obligatory | str | description of the model
  'description'
)
