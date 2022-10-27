from django.conf import settings
from django.core.files.storage import FileSystemStorage
from pathlib import Path


class OverwriteStorage(FileSystemStorage):

  def get_available_name(self, name, max_length=None):
    if self.exists(name):
      if settings.MEDIA_ROOT:
        Path.unlink(Path(settings.MEDIA_ROOT) / name)
      else:
        Path.unlink(Path(name))
    return name
