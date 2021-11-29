import time
from jose import jwk, jwt
from jose.utils import base64url_decode
from quart import current_app
from re import split

"""
AWS Cognito ID Token Payload
    {
    "sub": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "aud": "xxxxxxxxxxxxexample",
    "email_verified": true,
    "token_use": "id",
    "auth_time": 1500009400,
    "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_example",
    "cognito:username": "janedoe",
    "exp": 1500013000,
    "given_name": "Jane",
    "iat": 1500009400,
    "email": "janedoe@example.com",
    "jti": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "origin_jti": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    }
"""

class JWTExtendedException(Exception):
    """
    Base except which all errors extend
    """

    pass


class JWTDecodeError(JWTExtendedException):
    """
    An error decoding a JWT
    """

    pass


class InvalidHeaderError(JWTExtendedException):
    """
    An error getting header information from a request
    """

    pass


class NoAuthorizationError(JWTExtendedException):
    """
    An error raised when no authorization token was found in a protected
    endpoint
    """

    pass


def _decode_jwt_from_headers(req):
    header_name = 'Authorization'
    header_type = 'Bearer'

    # Verify we have the auth header
    auth_header = req.headers.get(header_name, "").strip().strip(",")
    if not auth_header:
        raise NoAuthorizationError(f"Missing {header_name} Header")

    # Make sure the header is in a valid format that we are expecting, ie
    # <HeaderName>: <HeaderType(optional)> <JWT>.
    #
    # Also handle the fact that the header that can be comma delimited, ie
    # <HeaderName>: <field> <value>, <field> <value>, etc...
    if header_type:
        field_values = split(r",\s*", auth_header)
        jwt_headers = [s for s in field_values if s.split()[0] == header_type]
        if len(jwt_headers) != 1:
            msg = (
                f"Missing '{header_type}' type in '{header_name}' header. "
                f"Expected '{header_name}: {header_type} <JWT>'"
            )
            raise NoAuthorizationError(msg)

        parts = jwt_headers[0].split()
        if len(parts) != 2:
            msg = (
                f"Bad {header_name} header. "
                f"Expected '{header_name}: {header_type} <JWT>'"
            )
            raise InvalidHeaderError(msg)

        encoded_token = parts[1]
    else:
        parts = auth_header.split()
        if len(parts) != 1:
            msg = f"Bad {header_name} header. Expected '{header_name}: <JWT>'"
            raise InvalidHeaderError(msg)

        encoded_token = parts[0]

    return encoded_token


def cognito_verify_token(token: str):
    keys = current_app.config['COGNITO_KEYS']
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    public_key = jwk.construct(keys[key_index])  # construct the public key
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != current_app.config['COGNITO_APP_CLIENT_ID']:
        print('Token was not issued for this audience')
        return False

    return claims


def verify_jwt(request):
    return cognito_verify_token(_decode_jwt_from_headers(request))
