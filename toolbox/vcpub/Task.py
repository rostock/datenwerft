import json
import logging

from datetime import datetime, timezone, timedelta
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
    source = Datasource(name=self.name, description=self.description)
    self.parameters['dataset'] = bucket.link()
    self.parameters['datasource'] = source.link()
    current_time = datetime.now(timezone.utc)
    scheduled_time = current_time + timedelta(minutes=30)
    self.schedule = {
      'type': 'scheduled',
      'scheduled': f'{scheduled_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}'
    }
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
    ok, task = self.__api.post(endpoint=f'/project/{self.__project_id}/task/', json=data)
    self._id = task['_id']
    pprint(self.__api.get(endpoint=f'/project/{self.__project_id}/data-bucket/{bucket.get_id()}'))

  def __get_task__(self):
    ok, task = self.__api.get(endpoint=f'/project/{self.__project_id}/task/{self._id}/')
    self.name = task['name']
    self.jobType = task['jobType']
    self.parameters = task['parameters']
    self.schedule = task['schedule']

  def get_dataset(self):
    """
    get dataset of a task.
    :return:
    """
    return self.parameters['dataset']

  def get_datasource(self):
    """
    get dataset of a task.
    :return:
    """
    return self.parameters['datasource']

  def get_endpoint(self):
    """
    get api endpoint of task object
    :return:
    """
    return f'/project/{self.__project_id}/task{self._id}'

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
    return self.__api.get_url() + self.get_endpoint()