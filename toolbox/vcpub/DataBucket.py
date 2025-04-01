from pathlib import Path
from uuid import uuid4

from toolbox.vcpub.vcpub import VCPub


class DataBucket:
  """
  This class implements the structure of DataBuckets of the VC Publisher API.

  :ivar __api: VCPub: API object of the VC Publisher API
  :ivar _id: str: ID of the data bucket
  :ivar name: str: Name of the data bucket
  :ivar description: str: Description of the data bucket
  :ivar properties: dict: Properties of the data bucket
  """

  _id: str = ''
  name: str = ''
  description: str = ''
  properties: dict = {}

  def __init__(
    self,
    _id: str = None,
    name: str = str(uuid4()),
    description: str = '',
    properties: dict = None,
    api: VCPub = None,
  ):
    if properties is None:
      properties = {}
    if api:
      self.__api = api
    else:
      self.__api = VCPub()
    self.__project_id = self.__api.get_project_id()
    if _id is not None:
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
      'properties': self.properties,
    }
    ok, bucket = self.__api.post(endpoint=f'/project/{self.__project_id}/data-bucket/', data=data)
    if ok:
      self._id = bucket['_id']
      self.name = bucket['name']
      self.create_object(key='.keep')
      self.__api.logger.debug('Data Bucket created.')
    else:
      self.__api.logger.warning(f'Failed to create Bucket. {bucket.__dict__}')

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
      self.__api.logger.warning(f'Failed to get Bucket. {bucket.__dict__}')

  def create_object(self, key: str, object_type: str = 'file'):
    """
    create an empty bucket object
    :param key:
    :param object_type:
    :return:
    """
    data = {'key': key, 'type': object_type}
    self.__api.post(endpoint=f'/project/{self.__project_id}/data_bucket/{self._id}', json=data)

  def delete(self):
    """
    delete Bucket
    :return:
    """
    endpoint = f'/project/{self.__project_id}/data-bucket/{self._id}'
    ok, response = self.__api.delete(endpoint=endpoint)
    return ok, response

  def download_file(self, object_key: str, stream: bool = True):
    """

    :return:
    """
    parameter = {'key': object_key}
    ok, response = self.__api.get(
      endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}/download-file',
      # headers=headers,
      stream=stream,
      params=parameter,
    )
    if not ok:
      self.__api.logger.warning(f'Failed to download file: {response.__dict__}')
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
    data = {'type': 'internal', 'dataBucketId': self._id, 'dataBucketKey': '/'}
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
      key = Path(path).name  # filename as key
      file = {key: open(path, 'rb')}
    ok, response = self.__api.post(
      endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}/upload',
      files=file,
      # stream=True
      # celery job runs for every chunk with stream option
    )
    if not ok:
      self.__api.logger.warning(f'Failed to upload file: {response.__dict__}')
    # return data-bucket object key of uploadet file
    key = f'/{key}'
    return ok, key

  def delete_object(self, key):
    params = f'?key={key}'
    ok, response = self.__api.delete(
      endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}/object{params}',
    )
    if not ok:
      self.__api.logger.warning(f'Failed to delete object: {response.__dict__}')
    return ok, response
