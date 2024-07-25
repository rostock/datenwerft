from uuid import uuid4

from toolbox.vcpub.DataBucket import DataBucket
from toolbox.vcpub.vcpub import VCPub


class Datasource:
  _id: str = ''
  name: str = ''
  description: str = ''
  typeProperties: dict = {}
  sourceProperties: dict = {}
  type: str = 'tileset'

  def __init__(self,
               _id: str = None,
               name: str = str(uuid4()),
               description: str = ''):
    if _id:
      self._id = _id
      self.__get_source__()
    else:
      self.name = f'{name}_source'
      self.description = description
      sourceBucket = DataBucket(name=self.name, description=self.description)
      self.sourceProperties = sourceBucket.link()
      self.__create__()

  def __create__(self):
    api = VCPub()
    data = {
      'name': self.name,
      'description': self.description,
      'typeProperties': self.typeProperties,
      'sourceProperties': self.sourceProperties,
      'type': self.type
    }
    source = api.post(endpoint=f'/project/{api.get_project_id()}/datasource/', data=data)
    self._id = source['_id']

  def __get_source__(self):
    api = VCPub()
    source = api.get(endpoint=f'/project/{api.get_project_id()}/datasource/{self._id}/')
    self.name = source['name']
    self.description = source['description']
    self.typeProperties = source['typeProperties']
    self.sourceProperties = source['sourceProperties']
    self.type = type

  def link(self):
    data = {
      'command': 'update',
      'datasourceId': self._id
    }
    return data
