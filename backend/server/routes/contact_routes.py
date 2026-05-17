from flask_restx import Namespace, Resource, fields
from flask import request
from server.services.email_service import EmailService
from server.factories.main_factory import MainFactory
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
    def post(self):
        """Submit a contact form"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'email', 'subject', 'message']
            for field in required_fields:
                if not data.get(field):
                    return {'message': f'{field} is required'}, 400
            
            # Get email service
            email_service = main_factory.get_email_service()
            
            # Send contact email
            success = email_service.send_contact_email(
                name=data['name'],
                email=data['email'],
                phone=data.get('phone', ''),
                subject=data['subject'],
                message=data['message']
            )
            
            if success:
                return {'message': 'Contact form submitted successfully'}, 200
            else:
                return {'message': 'Failed to send contact email'}, 500
                
        except Exception as e:
            logger.error("Error in contact form submission: %s", str(e), exc_info=True)
            return {'message': 'Internal server error'}, 500
