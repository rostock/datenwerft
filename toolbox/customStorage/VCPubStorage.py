import requests
from django.core.files.base import ContentFile
from django.core.files.storage import Storage

from toolbox.vcpub.DataBucket import DataBucket
from toolbox.vcpub.Task import Task
from toolbox.vcpub.vcpub import VCPub


class VCPubBucketStorage(Storage):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def _save(self, name, content, task_id: str, pointcloud_id: str):
    """
    Save File in Dataset Bucket of Task with task_id
    :param name:
    :param content:
    :param task_id:
    :return:
    """
    # get Task and Bucket informations
    task = Task(_id=task_id)
    bucket_id = task.get_dataset()['dataBucketId']
    bucket = DataBucket(_id=bucket_id)
    # upload file to dataset bucket
    file = {pointcloud_id: (content.read())}
    key = bucket.upload(file=file)
    return key, bucket.get_endpoint()

  def url(self, key):
    url = ''
    return url

  def exists(self, name):
    # Prüfen, ob die Datei existiert
    response = requests.head(name)
    return response.status_code == 200
