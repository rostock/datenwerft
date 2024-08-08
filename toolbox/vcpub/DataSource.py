import json
from pprint import pprint
from uuid import uuid4

from toolbox.vcpub.DataBucket import DataBucket
from toolbox.vcpub.vcpub import VCPub


class Datasource:
  __api: VCPub = VCPub()
  __project_id = __api
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
      source_bucket = DataBucket(name=self.name, description=self.description)
      self.sourceProperties = source_bucket.link()
      self.__create__()

  def __create__(self):
    """
    create datasource at VCPub API
    :return:
    """
    data = {
      'name': self.name,
      'description': self.description,
      'typeProperties': self.typeProperties,
      'sourceProperties': self.sourceProperties,
      'type': self.type
    }

    print('=====  CREATE DATASOURCE  =====')
    source = self.__api.post(endpoint=f'/project/{self.__project_id}/datasource', json=data)
    self._id = source['_id']

  def __get_source__(self):
    """
    get datasource informations from VCPub API of an existing datasource
    :return:
    """
    source = self.__api.get(endpoint=f'/project/{self.__project_id}/datasource/{self._id}')
    self.name = source['name']
    self.description = source['description']
    self.typeProperties = source['typeProperties']
    self.sourceProperties = source['sourceProperties']
    self.type = type

  def link(self):
    """
    create datasource link object as dict
    :return:
    """
    data = {
      'command': 'update',
      'datasourceId': self._id
    }
    return data

  def delete(self):
    """
    delete Datasource
    :return:
    """
    # delete datasource bucket
    bucket = DataBucket(_id=self.sourceProperties['dataBucketId'])
    bucket.delete()
    # delete source
    self.__api.delete(endpoint=f'/project/{self.__project_id}/datasource')
    # delete source object
    global_ref = globals()
    for var_name, var_obj in list(global_ref.items()):
      if var_obj is self:
        del global_ref[var_name]

  def get_endpoint(self):
    """
    get api endpoint of datasource object
    :return:
    """
    return f'/project/{self.__project_id}/datasource/{self._id}'

  def get_url(self):
    """
    get API URL of this datasource
    :return:
    """
    return self.__api.get_url() + self.get_endpoint()
