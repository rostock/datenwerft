from uuid import uuid4

from toolbox.vcpub.DataBucket import DataBucket
from toolbox.vcpub.vcpub import VCPub


class Datasource:
  """
  Implements the structure of a datasource object in the VC Publisher API.

  :ivar _id: str: ID of the datasource
  :ivar name: str: Name of the datasource
  :ivar description: str: Description of the datasource
  :ivar typeProperties: dict: Properties of the datasource
  :ivar sourceProperties: dict: Properties of the source
  """
  _id: str = ''
  name: str = ''
  description: str = ''
  typeProperties: dict = {}
  sourceProperties: dict = {}
  type: str = 'tileset'

  def __init__(self, _id: str = None, name: str = str(uuid4()),
               description: str = '', api: VCPub = None):
    if api:
      self.__api = api
    else:
      self.__api = VCPub()
    self.__project_id = self.__api.get_project_id()
    if _id:
      self._id = _id
      self.__get_source__()
    else:
      self.name = f'{name}_source'
      self.description = description
      source_bucket = DataBucket(name=self.name, description=self.description, api=self.__api)
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
    ok, source = self.__api.post(endpoint=f'/project/{self.__project_id}/datasource', json=data)
    if ok:
      self.__api.logger.debug('Data Source created.')
      self._id = source['_id']
    else:
      self.__api.logger.warning(f'Failed to create Data Source. {source.__dict__}')

  def __get_source__(self):
    """
    get datasource informations from VCPub API of an existing datasource
    :return:
    """
    ok, source = self.__api.get(endpoint=f'/project/{self.__project_id}/datasource/{self._id}')
    if ok:
      self.name = source['name']
      self.description = source['description']
      self.typeProperties = source['typeProperties']
      self.sourceProperties = source['sourceProperties']
      self.type = source['type']
    else:
      self.__api.logger.warning(f'Failed to get Data Source. {source.__dict__}')

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
    bucket = DataBucket(_id=self.sourceProperties['dataBucketId'], api=self.__api)
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
