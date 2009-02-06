AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
BUCKET_NAME = ''

try:
    from awskeys_local import *
except ImportError:
    pass
