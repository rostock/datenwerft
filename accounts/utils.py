import random

def get_client_ip(request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


LOWER_CASE_CHAR = 'abcdefghjkmnpqrstuvwxyz'
UPPER_CASE_CHAR = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
NUMBERS = '23456789'
SPECIAL_CHARACTERS = '§$%&/()=?#*+<>'
CODE_LENGTH = 4
CODE_CHARS = NUMBERS + UPPER_CASE_CHAR # do not use 1, i, l, 0, O, o, I and the SEGMENT_SEPARATOR
SEGMENT_LENGTH = 4
SEGMENT_SEPARATOR = '-'
PREFIX = None

def generate_key(
        prefix: str = PREFIX,
        codelength: int = CODE_LENGTH,
        segmented: str = SEGMENT_SEPARATOR,
        segmentlength: int = SEGMENT_LENGTH,
) -> str:
    key = "".join(random.choice(CODE_CHARS) for i in range(codelength))
    key = segmented.join(
        [key[i: i + segmentlength] for i in range(0, len(key), segmentlength)]
    )
    if not prefix:
        return key
    else:
        return prefix + key
