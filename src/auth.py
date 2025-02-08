import jwt
from datetime import datetime, timedelta
from functools import wraps
import streamlit as st
from .models import User
from config import Config

def create_jwt_token(user_id: int) -> str:
    expiry = datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRY_HOURS)
    return jwt.encode(
        {'user_id': user_id, 'exp': expiry},
        Config.SECRET_KEY,
        algorithm='HS256'
    )

def verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in st.session_state:
            st.error("Please login to access this feature")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def has_permission(permission):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            user = User.get_by_id(st.session_state.user_id)
            if user.has_permission(permission):
                return func(*args, **kwargs)
            st.error("You don't have permission to access this feature")
            st.stop()
        return wrapper
    return decorator