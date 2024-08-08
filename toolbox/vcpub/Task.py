import json
import logging
from pprint import pprint
from uuid import uuid4

from toolbox.vcpub.DataBucket import DataBucket
from toolbox.vcpub.DataSource import Datasource
from toolbox.vcpub.vcpub import VCPub


class Task:
  __api: VCPub = VCPub()
  __project_id = __api.get_project_id()
  _id: str = ''
  name: str = ''
  description: str = ''
  jobType: str = 'pointcloud'
  parameters: dict = {
    'epsgCode': 25833,
    'command': 'conversion',
    'dataset': {},
    'datasource': {}
  }
  schedule: dict = {
    'type': 'immediate'
  }

  def __init__(self,
               _id: str = None,
               name: str = str(uuid4()),
               description: str = ''):
    if _id:
      self._id = _id
      self.__get_task__()
    else:
      self.name = f'dw_{name.lower().replace(" ", "_")}'
      self.description = description
      self.__create__()


  def __create__(self):
    bucket = DataBucket(name=self.name, description=self.description)
    response = self.__api.get(
      endpoint=f'/project/{self.__project_id}/data-bucket/{bucket.get_id()}'
    )
    print(f'Bucket GET: {response}')
    source = Datasource(name=self.name, description=self.description)
    self.parameters['dataset'] = bucket.link()
    self.parameters['datasource'] = source.link()
    data = {
      'name': self.name,
      'description': self.description,
      'jobType': self.jobType,
      'parameters': self.parameters,
      'schedule': self.schedule
    }
    print(__name__)
    print('=====  CREATE TASK  =====')
    print(len(globals()))
    task = self.__api.post(endpoint=f'/project/{self.__project_id}/task/', json=data)
    self._id = task['_id']
    pprint(self.__api.get(endpoint=f'/project/{self.__project_id}/data-bucket/{bucket.get_id()}'))

  def __get_task__(self):
    task = self.__api.get(endpoint=f'/project/{self.__project_id}/task/{self._id}/')
    self.name = task['name']
    self.jobType = task['jobType']
    self.parameters = task['parameters']
    self.schedule = task['schedule']

  def delete(self):
    """
    delete task. Datasource is not deleted. It should be deleted manually via VC Publisher WEBGui,
    because it may contain live data from VC Map.
    :return:
    """
    # delete dataset bucket
    bucket_id = self.parameters['dataset']['dataBucketId']
    bucket = DataBucket(_id=bucket_id)
    bucket.delete()
    # delete task
    self.__api.delete(endpoint=f'/project/{self.__project_id}/task/{self._id}')
    # delete task object
    global_ref = globals()
    for var_name, var_obj in list(global_ref.items()):
      if var_obj is self:
        del global_ref[var_name]

  def get_dataset(self):
    """
    get dataset of a task.
    :return:
    """
    return self.parameters['dataset']

  def get_id(self):
    """
    get task id
    :return:
    """
    return self._id

  def get_url(self):
    """
    get API URL of this task
    :return:
    """
    baseurl = self.__api.get_url()
    url = f'{baseurl}/project/{self.__project_id}/task/{self._id}'
    return url