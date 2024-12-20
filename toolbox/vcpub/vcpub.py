import logging

from django.conf import settings
from toolbox.vcpub.BearerAuth import BearerAuth
from requests import Response, Session, post


class VCPub:
  logger = logging.getLogger('VCPub')

  def __init__(self):
    self.__user: str = settings.VCP_API_USER
    self.__password: str = settings.VCP_API_PASSWORD
    self.__project_id = settings.VCP_API_PROJECT_ID
    self.__data_path = '/vcs/data/public/'  # im root System unter /nfs/daten/rostock3d/vcpublisher
    self.__epsg = '25833'
    self.__connected = False

  def __del__(self):
    """
    extend deletion of VCPub object with logout.
    :return:
    """
    self.__logout__()

  def __login__(self) -> bool:
    """
    login at VCPub api
    :return: bearer token
    """
    if not self.__connected:
      bearer: str = 'no bearer'
      self.__url: str = settings.VCP_API_URL
      if self.__url:
        response: Response = post(
          url=f'{self.__url}/login/',
          data={
            "username": self.__user,
            "password": self.__password
          })
        if response.ok:
          bearer: str = response.json()['token']
          self.__auth = BearerAuth(bearer)
          self.__session = Session()
          self.__session.auth = self.__auth
          self.__connected = True
          self.logger.debug('VCPub Login.')
        else:
          self.logger.error(f'VCPub Login failed. {response.__dict__}')
    return self.__connected

  def __logout__(self) -> None:
    if self.__connected:
      response = self.__session.get(url=f'{self.__url}/logout/')
      if response.ok:
        self.logger.debug('Logout.')
      else:
        self.logger.warning(f'Logout failed: {response.json()}')

  def __logout_all__(self) -> None:
    if self.__connected:
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

  def post(self, endpoint: str, data: dict = None, json=None, files=None,
           *args, **kwargs) -> tuple[bool, dict | Response | None]:
    """
    Make a POST Request to the VC Publisher API.

    :param endpoint: api endpoint like `/project/`
    :param data: dictionary delivered in request body
    :param json:
    :param files:
    :return:
    """
    def post_it():
      url: str = self.__url + endpoint
      response = self.__session.post(url=url, data=data, json=json, files=files, *args, **kwargs)
      if response.ok and response.status_code != 204:
        self.logger.debug(f'POST on {url} succeeded. STATUS: {response.status_code}')
        return response.ok, response.json()
      elif response.status_code == 204:
        # 204 No Response
        self.logger.debug(f'POST on {url} succeeded. STATUS: {response.status_code}')
        return response.ok, None
      else:
        self.logger.warning(f'POST on {url} failed: {response.__dict__}')
        return response.ok, response

    if self.__connected:
      return post_it()
    else:
      if self.__login__():
        return post_it()
      else:
        response = Response()
        response.status_code = 502
        response.reason = 'Bad Gateway. VCPub Object is not connected.'
        return False, response

  def get(self, endpoint: str, headers=None, stream: bool = False,
          *args, **kwargs) -> tuple[bool, dict | Response | None]:
    """
    Make a GET Request to the VC Publisher API.

    :param endpoint: api endpoint like `/projects/`
    :param headers:
    :param stream: just for file downloads, default False
    :return: Response as dict
    """
    def get_it():
      url: str = self.__url + endpoint
      response = self.__session.get(url=url, headers=headers, stream=stream, *args, **kwargs)

      if response.ok and response.status_code != 204:
        self.logger.debug(f'GET on {url} succeeded. STATUS: {response.status_code}')
        if stream:
          return response.ok, response
        else:
          return response.ok, response.json()
      elif response.status_code == 204:
        # 204 No Response
        self.logger.debug(f'GET on {url} succeeded. STATUS: {response.status_code}')
        return response.ok, None
      else:
        self.logger.warning(f'GET on {url} failed: {response.json()}')
        return response.ok, response

    if self.__connected:
      return get_it()
    else:
      if self.__login__():
        return get_it()
      else:
        response = Response()
        response.status_code = 502
        response.reason = 'Bad Gateway. VCPub Object is not connected.'
        return False, response

  def delete(self, endpoint: str, headers=None) -> tuple[bool, dict | Response | None]:
    """
    Make a DELETE Request to the VC Publisher API.

    :param endpoint: api endpoint like `/project/<project_id>/`
    :param headers: json like dict
    :return: Response as dict
    """
    def delete_it():
      url: str = self.__url + endpoint
      response = self.__session.delete(url=url, headers=headers)
      if response.ok and response.status_code != 204:
        self.logger.debug(f'DELETE on {url} succeeded. STATUS: {response.status_code}')
        return response.ok, response.json()
      elif response.status_code == 204:
        # 204 No Response
        self.logger.debug(f'DELETE on {url} succeeded. STATUS: {response.status_code}')
        return response.ok, None
      else:
        self.logger.warning(f'DELETE on {url} failed: {response.json()}')
        return response.ok, response

    if self.__connected:
      return delete_it()
    else:
      if self.__login__():
        return delete_it()
      else:
        response = Response()
        response.status_code = 502
        response.reason = 'Bad Gateway. VCPub Object is not connected.'
        return False, response
