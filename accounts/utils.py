import ipaddress
import random


def get_client_ip(request):
  """
  determines the client IP address
  by investigating the client request

  :param request: client request
  :return: client IP address
  """
  x_forwarded_for = request.headers.get("X-Forwarded-For")
  if x_forwarded_for:
    ip = x_forwarded_for.split(",")[0]
  else:
    ip = request.META.get("REMOTE_ADDR")
  return ip


def validate_ip(ip_string):
  """
  validates an IP string,
  i.e. determines whether it is a valid IP address or not

  :param ip_string: IP string
  :return: IP string is a valid IP address?
  """
  try:
    ipaddress.ip_address(ip_string)
    return True
  except ValueError:
    return False


def validate_cidr(ip_string):
  """
  validates an IP string,
  i.e. determines whether it is a valid CIDR notation or not

  :param ip_string: IP string
  :return: IP string is a valid CIDR notation?
  """
  try:
    ipaddress.ip_network(ip_string)
    if not validate_ip(ip_string):
      return True
    else:
      return False
  except ValueError:
    return False


def ip_to_binary(ip_string):
  """
  converts an IP string to its binary representation

  :param ip_string: IP string
  :return: binary representation of IP string
  """
  octet_list_int = ip_string.split(".")
  octet_list_bin = [format(int(i), '08b') for i in octet_list_int]
  binary = "".join(octet_list_bin)
  return binary


def get_ip_network(ip_string, net_size):
  """
  returns the network of an IP string
  by means of the network size

  :param ip_string: IP string
  :param net_size: network size
  :return: network of IP string
  """
  # convert IP address to 32-bit binary
  ip_bin = ip_to_binary(ip_string)
  # extract network ID from 32-bit binary
  network = ip_bin[0:32 - (32 - net_size)]
  return network


def ip_in_prefix(ip_string, prefix):
  """
  determines whether an IP string
  is included in a prefix or not

  :param ip_string: IP string
  :param prefix: prefix
  :return: IP string is included in prefix or not?
  """
  # CIDR based separation of IP address and network size
  [prefix_address, net_size] = prefix.split("/")
  # convert string to int
  net_size = int(net_size)
  # get the network ID of both prefix and IP address based network size
  prefix_network = get_ip_network(prefix_address, net_size)
  ip_network = get_ip_network(ip_string, net_size)
  return ip_network == prefix_network


def ip_in_array(ip_string, ip_cidr_array):
  """
  determines whether an IP string
  is included in an array of IP strings and/or CIDR strings

  :param ip_string: IP string
  :param ip_cidr_array: array of IP strings and/or CIDR strings
  :return: client IP address
  """
  for array_item in ip_cidr_array:
    if ((validate_ip(array_item) and array_item == ip_string) or
        (validate_cidr(array_item) and ip_in_prefix(ip_string, array_item))):
      return True
  return False


LOWER_CASE_CHAR = 'abcdefghjkmnpqrstuvwxyz'
UPPER_CASE_CHAR = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
NUMBERS = '23456789'
SPECIAL_CHARACTERS = '§$%&/()=?#*+<>'
CODE_LENGTH = 4
CODE_CHARS = NUMBERS + UPPER_CASE_CHAR  # do not use 1, i, l, 0, O, o, I and the SEGMENT_SEPARATOR
SEGMENT_LENGTH = 4
SEGMENT_SEPARATOR = '-'
PREFIX = None


def generate_key(
    prefix: str = PREFIX,
    codelength: int = CODE_LENGTH,
    segmented: str = SEGMENT_SEPARATOR,
    segmentlength: int = SEGMENT_LENGTH,
) -> str:
  key = "".join(random.choice(CODE_CHARS) for _ in range(codelength))
  key = segmented.join(
    [key[i: i + segmentlength] for i in range(0, len(key), segmentlength)]
  )
  if not prefix:
    return key
  else:
    return prefix + key
