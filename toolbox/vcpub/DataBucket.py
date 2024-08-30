import os.path

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
    self._id = bucket['_id']
    self.name = bucket['name']


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
    self.__api.delete(endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}')
    global_ref = globals()
    for var_name, var_obj in list(global_ref.items()):
      if var_obj is self:
        del global_ref[var_name]

  def download_file(self):
    pass

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
      'dataBucketKey': self.name
    }
    return data

  def upload(self, path: str = None, file: dict = None):
    key = list(file.keys())[0]
    if path:
      key = os.path.basename(path) # filename as key
      file = {key: open(path, 'rb')}
    ok, response = self.__api.post(
      endpoint=f'/project/{self.__project_id}/data-bucket/{self._id}/upload',
      files=file
    )
    if not ok:
      print(response)
    # return data-bucket object key of uploadet file
    return ok, key

