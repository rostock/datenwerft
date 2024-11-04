import os.path

from django.http import FileResponse, HttpResponse, Http404
from docutils.nodes import header
from uaclient.api.u.pro.detach.v1 import endpoint

from toolbox.vcpub.vcpub import VCPub
from uuid import uuid4


class DataBucket:
  """
  This class implements the structure of DataBuckets of the VC Publisher API.
  """
  __api = VCPub()
  __project_id = __api.get_project_id()
  _id: str = ''
  name: str = ''
  description: str = ''
  properties: dict = {}


  def __init__(self,
               _id: str = None,
               name: str = str(uuid4()),
               description: str = '',
               properties: dict = {}):
    if _id:
      # get data bucket information for given id
      self._id = _id
      self.__get_bucket__()
    else:
      # create new data bucket
      self.name = f'{name}_bucket'
      self.description = description
      self.properties = properties
      self.__create__()

  def __create__(self) -> None:
    """
    This method registers a new data bucket in the VCPublisher API and takes over its data.
    :return:
    """
    data: dict = {
      'name': self.name,
      'description': self.description,
      'properties': self.properties
    }
    print('===== CREATE BUCKET =====')
    ok, bucket = self.__api.post(endpoint=f'/project/{self.__project_id}/data-bucket/', data=data)
    if ok:
      self._id = bucket['_id']
      self.name = bucket['name']
      self.create_object(key='.keep')


  def __get_bucket__(self):
    """
    This method takes the data from an existing data bucket.
    :return:
    """
    ok, bucket = self.__api.get(endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}')
    if ok:
      self.name = bucket['name']
      self.description = bucket['description']
      self.properties = bucket['properties']
      self.projectId = bucket['projectId']
    else:
      print(f'Respone ok?: {ok}')

  def create_object(self, key: str, type: str ='file'):
    """
    create an empty bucket object
    :param key:
    :param type:
    :return:
    """
    data = {
      'key': key,
      'type': type
    }
    self.__api.post(
      endpoint=f'/project/{self.__project_id}/data_bucket/{self._id}',
      json=data
    )

  def delete(self):
    """
    delete Bucket
    :return:
    """
    ok, response = self.__api.delete(endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}')
    return ok, response

  def download_file(self, object_key: str, stream: bool=True):
    """

    :return:
    """
    parameter = {
      "key": object_key
    }
    #print(headers)
    ok, response = self.__api.get(
      endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}/download-file',
      #headers=headers,
      stream=stream,
      params=parameter
    )
    print(response.raw.__dict__)
    return ok, response




  def get_endpoint(self):
    """
    get api endpoint of databucket object
    :return:
    """
    return f'/project/{self.__project_id}/data-bucket/{self._id}'

  def get_id(self):
    """
    Returns the ID of the data bucket object.
    :return:
    """
    return self._id

  def get_key(self):
    """
    Returns the key of the data bucket object.
    :return:
    """
    return self.name

  def get_name(self):
    """
    Returns the name of the data bucket object.
    :return:
    """
    return self.name

  def get_url(self):
    """
    get API URL of this data bucket object
    :return:
    """
    return self.__api.get_url() + self.get_endpoint()

  def link(self) -> dict:
    """
    generate bucket information to link this object in tasks or sources

    :return:
    """
    data = {
      'type': 'internal',
      'dataBucketId': self._id,
      'dataBucketKey': '/'
    }
    return data

  def upload(self, path: str = None, file: dict = None):
    """
    Uploads a file to the data bucket.

    :param path: path to uploaded file
    :param file: or file
    :return:
    """
    key = list(file.keys())[0]
    if path:
      key = os.path.basename(path) # filename as key
      file = {key: open(path, 'rb')}
    ok, response = self.__api.post(
      endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}/upload',
      files=file
      #stream=True
      # celery job runs for every chunk with stream option
    )
    if not ok:
      print(response)
    # return data-bucket object key of uploadet file
    key = f'/{key}'
    return ok, key

  def delete_object(self, key):
    params=f'?key={key}'
    ok, response = self.__api.delete(
      endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}/object{params}',
    )
    return ok, response
