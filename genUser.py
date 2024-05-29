import json
import base64
import hmac
import hashlib
import random

SECRET = 'your_secret_key_here' # Add your secret key here


def base64UrlEncode(data):
    return base64.urlsafe_b64encode(data.encode('utf-8')).rstrip(b'=').decode('utf-8')


def genSignature(source, secret):
    return base64.urlsafe_b64encode(
        hmac.new(secret.encode('utf-8'), source.encode('utf-8'), hashlib.sha256).digest()).rstrip(b'=').decode('utf-8')


def genJwtToken(payload, secret):
    header = base64UrlEncode(json.dumps({
        "alg": "HS256",
        "typ": "JWT"
    }))

    payload = base64UrlEncode(json.dumps(payload))

    unsignedToken = f"{header}.{payload}"

    signature = genSignature(unsignedToken, secret)

    return f"{unsignedToken}.{signature}"


emails = ["your_email_address"]  # Add your email address here


def gen(email):
    googleIdToken = genJwtToken({"email": email}, SECRET)
    return {
        "googleIdToken": googleIdToken,
        "googleVerifyToken": googleIdToken.split('.')[-1],
        "googleAccessToken": "no"
    }
