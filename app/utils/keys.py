from collections import OrderedDict
from flask import current_app
from itsdangerous import (
    TimedJSONWebSignatureSerializer as TimedToken,
    JSONWebSignatureSerializer as Token,
    BadData, BadSignature, SignatureExpired
    )

from ..models import Member

__all__ = [
    'PrivateKey', 'PublicKey', 'verify_public_key',
    'hmac', 'verify_hmac'
    ]

def PrivateKey(id):
    '''Generate a reusable private key for the user.'''
    t = Token(secret_key=current_app.config['SECRET_KEY'])
    return t.dumps({'id':id})

def PublicKey(id):
    '''Generate an expiring public key for the user.'''
    t = TimedToken(
        secret_key=current_app.config['SECRET_KEY'],
        expires_in=current_app.config.get('TOKEN_DURATION', 3600)
        )
    return s.dumps({'id':id})

def verify_public_key(token):
    '''Attempt to validate a public key.'''
    t = TimedToken(
        secret_key=current_app.config['SECRET_KEY'],
        expires_in=current_app.config.get('TOKEN_DURATION', 3600)
        )
    try:
        data = t.loads(token)
    except (BadSignature, SignatureExpired):
        # Don't give away more information than needed
        # Just say, "You gave me a bad public key."
        raise BadData("Invalid public key.")
    else:
        return Member.query.get(data['id'])


def organize_payload(payload):
    '''Organizes the payload for consistency in
    communications between server and client.
    '''
    payload = sorted(list(payload.items()))
    return OrderedDict(payload)

def hmac(payload, private_key):
    '''Generate a decryptable signature on the server side that the client
    can analzye. Server generated HMAC signatures aren't timed.
    '''
    payload = organize_payload(payload)
    t = Token(secret_key=private_key)
    return t.dumps(payload)

def verify_hmac(hmac, public_key, payload):
    '''Attempt to verify a payload sent by a client. Client payloads are
    encrypted with their private key and timed to prevent replay.
    '''
    member = verify_public_key(public_key)
    if not member:
        # Don't give away more information than needed
        # Just say, "You didn't give us a valid public key."
        raise BadData("Invalid public key.")
    
    private_key = PrivateKey(member.id)
    payload = organize_payload(payload)
    t = TimedToken(
        secret_key=private_key, 
        expires_in=current_app.config.get('HMAC_DURATION', 5)
        )
    return t.loads(hmac) == payload
      
