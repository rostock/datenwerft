import logging
import pprint
import time

import requests

from datenwerft import settings
from toolbox.vcpub.BearerAuth import BearerAuth
from requests import Response, Session, post


class VCPub:
  logger = logging.getLogger('VCPub')

  def __init__(self):
    self.__user: str = settings.VCP_API_USER
    self.__password: str = settings.VCP_API_PASSWORD
    self.__url: str = settings.VCP_API_URL
    self.__project_id = settings.VCP_API_PROJECT_ID
    # Authenticate and create es session
    self.__auth: BearerAuth = self.__login__()
    self.__session: Session = Session()
    self.__session.auth = self.__auth
    self.__data_path = '/vcs/data/public/' # im root System unter /nfs/daten/rostock3d/vcpublisher
    self.__epsg = '25833'

  def __del__(self):
    """
    extend deletion of VCPub object with logout.
    :return:
    """
    self.__session.get(url=f'{self.__url}/logout/')

  def __login__(self) -> BearerAuth:
    """
    login at VCPub api
    :return: bearer token
    """
    response: Response = post(
      url=f'{self.__url}/login/',
      data={
        "username": self.__user,
        "password": self.__password
      })
    if response.ok:
      bearer: str = response.json()['token']
      self.logger.debug('Login.')
    else:
      bearer: str = 'no bearer'
      self.logger.error(f'Login Failed: {response.json()}')
    return BearerAuth(bearer)

  def __logout__(self) -> bool:
    response = self.__session.get(url=f'{self.__url}/logout/')
    if response.ok:
      self.logger.debug('Logout.')
    else:
      self.logger.warning(f'Logout failed: {response.json()}')

  def __logout_all__(self) -> bool:
    response = self.__session.get(url=f'{self.__url}/logout-all/')
    if response.ok:
      self.logger.debug('Logout all.')
    else:
      self.logger.warning(f'Logout all failed: {response.json()}')

  def get_url(self) -> str:
    return self.__url

  def get_project_id(self) -> str:
    """
    get project id of VCPub project.
    :return:
    """
    return self.__project_id

  def post(self, endpoint:str, data:dict = None, json=None, files=None) -> tuple[bool, dict|requests.Response|None]:
    """
    Make a POST Request to the VC Publisher API.

    :param endpoint: api endpoint like `/project/`
    :param data: dictionary delivered in request body
    :param json:
    :param files:
    :return:
    """
    url: str = self.__url + endpoint
    response = self.__session.post(url=url, data=data, json=json, files=files)
    print(response.__dict__)
    if response.ok and response.status_code is not 204:
      self.logger.debug(f'POST {url}')
      return response.ok, response.json()
    elif response.status_code is 204:
      self.logger.debug(f'POST {url}')
      return response.ok, None
    else:
      self.logger.warning(f'POST on {url} failed: {response.__dict__}')
      return response.ok, response

  def get(self, endpoint: str) -> tuple[bool, dict]:
    """
    Make a GET Request to the VC Publisher API.

    :param endpoint: api endpoint like `/projects/`
    :return: Response as dict
    """
    url: str = self.__url + endpoint
    response = self.__session.get(url=url)
    if response.ok:
      self.logger.debug(f'GET {url}')
      return response.ok, response.json()
    else:
      self.logger.warning(f'GET on {url} failed: {response.json()}')
      return response.ok, response

  def delete(self, endpoint: str) -> tuple[bool, dict]:
    """
    Make a DELETE Request to the VC Publisher API.

    :param endpoint: api endpoint like `/project/<project_id>/`
    :return: Response as dict
    """
    url: str = self.__url + endpoint
    response = self.__session.delete(url=url)
    if response.ok:
      self.logger.debug(f'DELETE {url}')
      return response.ok, response.json()
    else:
      self.logger.warning(f'DELETE on {url} failed: {response.json()}')
      return response.ok, response

  def create_data_bucket(self, name: str) -> dict:
    """
    Create a new date bucket for input files

    :param name: Name of the bucket
    :return:
    """
    data: dict = {
      'name': f'dw_{name.lower().replace(" ", "_")}_bucket'
    }
    ok, response = self.post(endpoint=f'/project/{self.__project_id}/data-bucket/', data=data)
    return response

  def delete_data_bucket(self, bucket_id: str) -> dict:
    """
    deletes a data bucket

    :param bucket_id: of the bucket to be deleted.
    :return:
    """
    ok, response = self.delete(endpoint=f'/project/{self.__project_id}/data-bucket/{bucket_id}/')
    return response

  def create_datasource(self,
                        name: str,
                        description: str = "",
                        dataBucketId: str = None,
                        dataBucketKey: str = None,) -> dict:
    """
    Creates a new datasource.

    :param name: name of the datasource > will be converted to 'crazy_datasource_name_source'
    :param description: optional, description of the datasource
    :param dataBucketId: optional, dataBucketId of an existing data bucket
    :param dataBucketKey: optional, dataBucketKey of an existing data bucket
    :return:
    """
    datasource_name = f'{name.lower().replace(" ", "_")}_source'
    if not dataBucketId:
      new_bucket = self.create_data_bucket(name=datasource_name)
      dataBucketId = new_bucket['_id']
      dataBucketKey = new_bucket['name']
    data: dict = {
      'name': f'dw_{datasource_name}',
      'description': description,
      'typeProperties': {},
      'sourceProperties': {
        'type': 'internal',
        'dataBucketId': f'{dataBucketId}',
        'dataBucketKey': f'{dataBucketKey}'
      },
      'type': 'tileset'
    }
    ok, response = self.post(endpoint=f'/project/{self.__project_id}/datasource/', data=data)
    return response

  def create_task(self,
                  name: str,
                  description: str = "",
                  inputBucketId: str = None,
                  inputBucketKey: str = None,
                  datasourceId: str = None,
                  **kwargs):
    """
    Create a new task.
    :param name: name of the task
    :param description: optional description
    :param inputBucketId: optional, data bucket id (default: create new bucket)
    :param inputBucketKey: optional,
    :param datasourceId: optional datasource id (default: create new datasource)
    :param kwargs: define 'uuid' to set the datasource folder name
    :return:
    """
    data = {
      'name': f'dw_{name}',
      'description': description,
      'parameters': {
        'epsgCode': self.__epsg,
        'command': 'conversion',
        'dataset': {
          'dataBucketId': f'{inputBucketId}',
          'dataBucketKey': f'{inputBucketKey}'
        },
        'datasource': {
          'command': 'update',
          'datasourceId': f'{datasourceId}'
        }
      },
      'jobType': 'pointcloud',
      'schedule': {
        'type': 'immediate'
      }
    }
    if not inputBucketId:
      # create data bucket if not given
      response = self.create_data_bucket(name=name)
      new_bucket_id = response['_id']
      new_bucket_name = response['name']
      data['parameters']['dataBucket']['dataBucketId'] =  new_bucket_id
      data['parameters']['dataBucket']['dataBucketKey'] = new_bucket_name
    if not datasourceId:
      # create datasource if not given
      if kwargs['uuid']:
        r = self.create_datasource(name=name, folder_name=kwargs['uuid'])
        time.sleep(2.5)
        pprint.pprint(r)
        new_source_id = r['_id']
      else:
        new_source_id = self.create_datasource(name=name)['_id']
      data['parameters']['datasource']['datasourceId'] = new_source_id
    ok, response = self.post(
      endpoint=f'/project/{self.__project_id}/task/',
      data=data
    )
    return response