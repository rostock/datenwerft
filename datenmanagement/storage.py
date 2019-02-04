# -*- coding: utf-8 -*-

from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            if settings.MEDIA_ROOT:
                os.remove(os.path.join(settings.MEDIA_ROOT, name))
            else:
                os.remove(name)
        return name
