from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
  """
  allows overwriting existing files with the same name
  """

  def __init__(
    self,
    location=None,
    base_url=None,
    file_permission_mode=None,
    directory_permissions_mode=None,
    path_root=settings.MEDIA_ROOT,
  ):
    super().__init__(
      location=location,
      base_url=base_url,
      file_permissions_mode=file_permission_mode,
      directory_permissions_mode=directory_permissions_mode,
    )
    self.path_root = path_root

  def get_available_name(self, name, max_length=None):
    if self.exists(name):
      if self.path_root:
        (Path(self.path_root) / name).unlink()
      else:
        Path(name).unlink()
    return name
