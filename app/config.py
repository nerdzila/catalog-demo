# TODO: This kind of secret shouldn't be in the repo
#
# It was left here as this is just a demo, but as soon as possible it should
# be replaced with a new token using:
#
#  openssl rand -hex 32
#
# .. and it shoud be passed via an environtment variable/secrets manager
# instead of being hardcoded
SECRET_KEY = "1ba0e35e30d02e5aae111f488a283447ce9897ddda3268ad6e6012ced8692797"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

FIRST_USER_EMAIL = "escribele.a.alfonso@gmail.com"
FIRST_USER_PASSWORD = "not_a_real_password"
