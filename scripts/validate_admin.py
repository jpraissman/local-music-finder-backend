from app import ADMIN_KEY
from collections.abc import Callable
from functools import wraps
from flask import request, jsonify

# This is a higher order function that confirms the request has the correct admin key to access the resource.
# If not, this function throws an Unauthorized error.
def validate_admin_key(f: Callable) -> Callable:
  @wraps(f)
  def decorated_function(*args, **kwargs):
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
      return jsonify({'error': 'You must be an admin to access this.'}), 401
    return f(*args, **kwargs)
  return decorated_function