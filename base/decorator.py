

from functools import wraps
from dotenv import load_dotenv
from flask import request


load_dotenv()

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "authorization" in request.headers:
            token = request.headers["authorization"]
        if not token:
            return {"status": 0, "message": "a valid token is missing"}
        try:

            
            if  token != '4b9dc01ff3f38b6ec5437ae8f1e686e16':
                return {"status": 0, "message": "token is invalid"}

        except:  # noqa: E722
            return {"status": 0, "message": "token is invalid"}

        return f(*args, **kwargs)

    return decorator

