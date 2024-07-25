from toolbox.vcpub.vcpub import VCPub
from uuid import uuid4


class DataBucket:
  """
  This class implements the structure of DataBuckets of the VC Publisher API.
  """
  _id: str = ''
  name: str = ''
  description: str = ''
  properties: dict = {}

  def __init__(self, _id: str = None, name: str = str(uuid4()), description: str = '', properties: dict = {}):
    if _id:
      # get data bucket information for given id
      self._id = _id
      self.__getdata__()
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
    api = VCPub()
    data: dict = {
      'name': self.name,
      'description': self.description,
      'properties': self.properties
    }
    bucket = api.post(endpoint=f'/project/{api.get_project_id()}/data-bucket/', data=data)
    self._id = bucket['_id']
    self.name = bucket['name']

  def __getdata__(self):
    """
    This method takes the data from an existing data bucket.
    :return:
    """
    api = VCPub()
    bucket = api.get(endpoint=f'/project/{api.get_project_id()}/data-bucket/{self._id}')
    self.name = bucket['name']
    self.description = bucket['description']
    self.properties = bucket['properties']
    self.projectId = bucket['projectId']

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

  def link(self) -> dict:
    """
    generate bucket information to link this object in tasks or sources
    :return:
    """
    data = {
      'type': 'internal',
      'dataBucketId': self._id,
      'databucketKey': self.name
    }
    return data