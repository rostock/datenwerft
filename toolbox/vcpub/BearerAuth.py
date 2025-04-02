import requests


class BearerAuth(requests.auth.AuthBase):
  """
  Extends the requests library with the option to authenticate with a bearer token at a Rest API.
  """

  def __init__(self, token: str):
    self.token: str = token

  def __call__(self, r):
    r.headers['authorization'] = 'Bearer ' + self.token
    return r
