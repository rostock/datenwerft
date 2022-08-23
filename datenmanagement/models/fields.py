from django import forms
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core import exceptions



# Quelle :https://gist.github.com/danni/f55c4ce19598b2b345ef

class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.TypedMultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)

    def to_python(self, value):
        res = super().to_python(value)
        if isinstance(res, list):
            value = [self.base_field.to_python(val) for val in res]
        else:
            value = None
        return value

    def validate(self, value, model_instance):
        if not self.editable:
            return

        if value is None or value in self.empty_values:
            return None

        if self.choices is not None and value not in self.empty_values:
            if set(value).issubset(
                    {option_key for option_key, _ in self.choices}):
                return
            raise exceptions.ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={
                    'value': value
                },
            )

        if value is None and not self.null:
            raise exceptions.ValidationError(
                self.error_messages['null'], code='null')

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(
                self.error_messages['blank'], code='blank')


class NullTextField(models.TextField):
    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if value is None or value in self.empty_values:
            return None
        elif isinstance(value, str):
            return value
        return str(value)

    def get_prep_value(self, value):
        value = super(NullTextField, self).get_prep_value(value)
        return self.to_python(value)

    def formfield(self, **kwargs):
        return super(NullTextField, self).formfield(**{
            'max_length': self.max_length,
            **({} if self.choices is not None else {'widget': forms.Textarea}),
            **kwargs,
        })


class PositiveIntegerRangeField(models.PositiveIntegerField):
    def __init__(
            self,
            verbose_name=None,
            name=None,
            min_value=None,
            max_value=None,
            **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.PositiveIntegerField.__init__(
            self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(PositiveIntegerRangeField, self).formfield(**defaults)


class PositiveIntegerMinField(models.PositiveIntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, **kwargs):
        self.min_value = min_value
        models.PositiveIntegerField.__init__(
            self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value}
        defaults.update(kwargs)
        return super(PositiveIntegerMinField, self).formfield(**defaults)


class PositiveSmallIntegerMinField(models.PositiveSmallIntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, **kwargs):
        self.min_value = min_value
        models.PositiveSmallIntegerField.__init__(
            self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value}
        defaults.update(kwargs)
        return super(PositiveSmallIntegerMinField, self).formfield(**defaults)


class PositiveSmallIntegerRangeField(models.PositiveSmallIntegerField):
    def __init__(
            self,
            verbose_name=None,
            name=None,
            min_value=None,
            max_value=None,
            **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.PositiveSmallIntegerField.__init__(
            self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(
            PositiveSmallIntegerRangeField,
            self).formfield(
            **defaults)
