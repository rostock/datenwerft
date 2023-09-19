from django.conf import settings
from django.core.files.storage import FileSystemStorage
from pathlib import Path


class OverwriteStorage(FileSystemStorage):
  """
  allows overwriting existing files with the same name
  """

  def get_available_name(self, name, max_length=None):
    if self.exists(name):
      if settings.MEDIA_ROOT:
        (Path(settings.MEDIA_ROOT) / name).unlink()
      else:
        Path(name).unlink()
    return name
