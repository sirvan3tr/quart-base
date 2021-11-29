from functools import wraps
from app.models import Permission
from app.cognito import verify_jwt
from quart import request, abort
from flask_login import current_user


def permission_required(permission):
    """Restrict a view to users with the given permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jwt_claim = verify_jwt(request)
        kwargs['jwt_claim'] = jwt_claim
        if jwt_claim is False:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function