from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base error class for custom API errors"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        logger.error(f"API Error: {error.message}")
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response = jsonify({
            'message': error.description,
            'status': 'error'
        })
        response.status_code = error.code
        logger.error(f"HTTP Error {error.code}: {error.description}")
        return response

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        response = jsonify({
            'message': 'Database error occurred',
            'status': 'error'
        })
        response.status_code = 500
        logger.error(f"Database Error: {str(error)}")
        return response

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        response = jsonify({
            'message': 'Data integrity error',
            'status': 'error'
        })
        response.status_code = 400
        logger.error(f"Integrity Error: {str(error)}")
        return response

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        response = jsonify({
            'message': 'An unexpected error occurred',
            'status': 'error'
        })
        response.status_code = 500
        logger.error(f"Unexpected Error: {str(error)}")
        return response

# Custom error classes
class ResourceNotFoundError(APIError):
    def __init__(self, message='Resource not found'):
        super().__init__(message=message, status_code=404)

class ValidationError(APIError):
    def __init__(self, message='Validation error'):
        super().__init__(message=message, status_code=400)

class AuthenticationError(APIError):
    def __init__(self, message='Authentication failed'):
        super().__init__(message=message, status_code=401)

class AuthorizationError(APIError):
    def __init__(self, message='Permission denied'):
        super().__init__(message=message, status_code=403)

class ConflictError(APIError):
    def __init__(self, message='Resource conflict'):
        super().__init__(message=message, status_code=409) 