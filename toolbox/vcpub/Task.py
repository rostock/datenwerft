from uuid import uuid4

from toolbox.vcpub.DataBucket import DataBucket
from toolbox.vcpub.DataSource import Datasource
from toolbox.vcpub.vcpub import VCPub


class Task:
  _id: str = ''
  name: str = ''
  description: str = ''
  jobType: str = 'pointcloud'
  parameters: dict = {
    'epsgCode': '25833',
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
      self.name = f'dw_{name}'
      self.description = description
      self.__create__()


  def __create__(self):
    api = VCPub()
    bucket = DataBucket(name=self.name, description=self.description)
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
    task = api.post(endpoint=f'/project/{api.get_project_id()}/task/', data=data)
    self._id = task['_id']

  def __get_task__(self):
    api = VCPub()
    task = api.get(endpoint=f'/project/{api.get_project_id()}/task/{self._id}/')
    self.name = task['name']
    self.jobType = task['jobType']
    self.parameters = task['parameters']
    self.schedule = task['schedule']
