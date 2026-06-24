from flask_restx import Namespace, Resource, fields
from flask import request
from server.services.email_service import EmailService
from server.factories.main_factory import MainFactory
from server.validation.input_validator import validate_email_input, validate_string_input
from server.middleware.rate_limit_middleware import rate_limit_by_ip
from server.routes.response_utils import error_response
import logging
# Module logger
logger = logging.getLogger(__name__)

# Create namespace
api = Namespace('contact', description='Contact form operations')

# Create main factory instance
main_factory = MainFactory()

# Define models
contact_form_model = api.model('ContactForm', {
    'name': fields.String(required=True, description='Full name'),
    'email': fields.String(required=True, description='Email address'),
    'phone': fields.String(description='Phone number'),
    'subject': fields.String(required=True, description='Subject'),
    'message': fields.String(required=True, description='Message content')
})

@api.route('/')
class ContactResource(Resource):
    @api.expect(contact_form_model)
    @api.doc('submit_contact_form')
    @rate_limit_by_ip('CONTACT_RATE_LIMIT_COUNT', 'CONTACT_RATE_LIMIT_WINDOW_SECONDS', 'contact-form')
    def post(self):
        """Submit a contact form"""
        try:
            data = request.get_json(silent=True)
            if not data:
                return error_response('Request body is required', 400)
            
            # Validate required fields
            required_fields = ['name', 'email', 'subject', 'message']
            for field in required_fields:
                if not data.get(field):
                    return error_response(f'{field} is required', 400)

            email_result = validate_email_input(data.get('email'))
            name_result = validate_string_input(data.get('name'), max_length=120)
            subject_result = validate_string_input(data.get('subject'), max_length=200)
            message_result = validate_string_input(data.get('message'), max_length=5000)

            if not email_result.is_valid:
                return error_response('Invalid email', 400)
            if not name_result.is_valid or not subject_result.is_valid or not message_result.is_valid:
                return error_response('Invalid name, subject, or message', 400)
            
            # Get email service
            email_service = main_factory.get_email_service()
            
            # Send contact email
            success = email_service.send_contact_email(
                name=name_result.sanitized_data,
                email=email_result.sanitized_data,
                phone=data.get('phone', ''),
                subject=subject_result.sanitized_data,
                message=message_result.sanitized_data
            )
            
            if success:
                return {'message': 'Contact form submitted successfully'}, 200
            else:
                return error_response('Failed to send contact email', 500, code='CONTACT_EMAIL_SEND_ERROR', category='external_api', retryable=True)
                
        except Exception as e:
            logger.error("Error in contact form submission", exc_info=True)
            return error_response('Internal server error', 500, category='system', retryable=True)
