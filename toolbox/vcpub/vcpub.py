import logging

from django.http import FileResponse

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
    self.__logout__()

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

  def __logout__(self) -> None:
    response = self.__session.get(url=f'{self.__url}/logout/')
    if response.ok:
      self.logger.debug('Logout.')
    else:
      self.logger.warning(f'Logout failed: {response.json()}')

  def __logout_all__(self) -> None:
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

  def post(self, endpoint:str, data:dict = None, json=None, files=None) -> tuple[bool, dict|Response|None]:
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
    if response.ok and response.status_code != 204:
      self.logger.debug(f'POST {url}')
      return response.ok, response.json()
    elif response.status_code == 204:
      # 204 No Response
      self.logger.debug(f'POST {url}')
      return response.ok, None
    else:
      self.logger.warning(f'POST on {url} failed: {response.__dict__}')
      return response.ok, response

  def get(self, endpoint: str, headers=None, stream: bool=False) -> tuple[bool, dict|Response|None]:
    """
    Make a GET Request to the VC Publisher API.

    :param endpoint: api endpoint like `/projects/`
    :param headers:
    :param stream: just for file downloads, default False
    :return: Response as dict
    """
    url: str = self.__url + endpoint
    response = self.__session.get(url=url, headers=headers, stream=stream)

    if response.ok and response.status_code != 204:
      self.logger.debug(f'GET {url}')
      if stream:
        return response.ok, response
      else:
        return response.ok, response.json()
    elif response.status_code == 204:
      # 204 No Response
      self.logger.debug(f'GET {url}')
      return response.ok, None
    else:
      self.logger.warning(f'GET on {url} failed: {response.json()}')
      return response.ok, response

  def delete(self, endpoint: str, headers=None) -> tuple[bool, dict|Response|None]:
    """
    Make a DELETE Request to the VC Publisher API.

    :param endpoint: api endpoint like `/project/<project_id>/`
    :param headers: json like dict
    :return: Response as dict
    """
    url: str = self.__url + endpoint
    response = self.__session.delete(url=url, headers=headers)
    if response.ok and response.status_code != 204:
      self.logger.debug(f'DELETE {url}')
      return response.ok, response.json()
    elif response.status_code == 204:
      # 204 No Response
      self.logger.debug(f'DELETE {url}')
      return response.ok, None
    else:
      self.logger.warning(f'DELETE on {url} failed: {response.json()}')
      return response.ok, response
