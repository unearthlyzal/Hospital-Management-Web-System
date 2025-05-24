from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request, jsonify, current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restx import Namespace, Api, Resource, fields as restx_fields
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_token(user_id: str, role: str) -> str:
    """
    Generate a JWT token for the user
    
    Args:
        user_id (str): The user's ID
        role (str): The user's role (Admin, Doctor, Patient)
        
    Returns:
        str: The generated JWT token
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    
    return jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY', 'your-secret-key-here'),
        algorithm='HS256'
    ) 