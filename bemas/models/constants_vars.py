from django.db.models import options

#
# custom meta attributes for models
#

options.DEFAULT_NAMES += (
  # optional;
  # Boolean;
  # is the model a codelist?
  'codelist'
)
