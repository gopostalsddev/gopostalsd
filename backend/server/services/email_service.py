import logging
from typing import Dict, Any, Optional
from flask import Flask
from markupsafe import escape as html_escape
from server.thirdparty.mailersend import MailerSendAdapter
from server.thirdparty.smtp import SMTPAdapter
from server.email_config import (
    BRAND_NAME,
    INTENDED_SENDER_ADDRESS,
    PLATFORM_ATTRIBUTION,
    load_email_settings,
)

logger = logging.getLogger(__name__)

class EmailService:
    """Email service implementation supporting multiple providers (MailerSend, SMTP)."""
    
    def __init__(self):
        self.client = None
        self.provider = None
        settings = load_email_settings()
        self.base_url = settings.public_base_url if settings else 'http://localhost:5173'
    
    def init_app(self, app: Flask, provider: Optional[str] = None):
        """
        Initialize email service with specified provider.
        
        Args:
            app: Flask application instance
            provider: Optional test/development override. Production uses EMAIL_PROVIDER.
        """
        # Determine provider
        settings = load_email_settings()
        self.provider = provider.lower() if provider else (settings.provider if settings else None)
        if not self.provider:
            logger.warning("No email provider configured; set EMAIL_PROVIDER")
            return
        
        try:
            if self.provider == 'mailersend':
                self.client = MailerSendAdapter()
                provider_name = "MailerSend"
            elif self.provider == 'smtp':
                self.client = SMTPAdapter()
                provider_name = "SMTP"
            else:
                logger.error("Unknown email provider configured")
                return
            
            if self.client.is_configured:
                logger.info(f"Email service initialized successfully with {provider_name}")
                logger.info(f"Frontend URL configured as: {self.base_url}")
            else:
                logger.warning(f"Email service initialized with {provider_name} but not configured")
                logger.info(f"Frontend URL configured as: {self.base_url}")
                
        except Exception:
            logger.exception("Failed to initialize configured email service")
            self.client = None
    
    def send_email(self, to_email: str, subject: str, text_content: str, html_content: str = None, reply_to: str = None) -> Dict[str, Any]:
        """
        Send email using the configured provider.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            text_content: Plain text content
            html_content: HTML content (optional)
            reply_to: Reply-to email address (optional, defaults to FROM_EMAIL)
        
        Returns:
            Dict containing send result
        """
        if not self.client:
            return {
                'success': False, 
                'error': 'Email service not configured. Set EMAIL_API_KEY environment variable.'
            }
        
        return self.client.send_email(to_email, subject, text_content, html_content, reply_to)
    
    @property
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return self.client and self.client.is_configured
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current email provider."""
        if not self.client:
            return {
                'provider': None,
                'configured': False,
                'error': 'No email provider configured'
            }
        
        info = {
            'provider': self.provider,
            'configured': self.client.is_configured,
            'from_email': self.client.get_from_email(),
            'from_name': self.client.get_from_name()
        }
        
        # Add provider-specific info
        if hasattr(self.client, 'get_smtp_info'):
            info.update(self.client.get_smtp_info())
        
        return info
    
    def send_verification_email(self, email: str, first_name: str, token: str, reply_to: str = None) -> Dict[str, Any]:
        """Send email verification email."""
        subject = f"Verify Your Email - {BRAND_NAME}"

        verification_url = f"{self.base_url}/#/verify?token={token}"
        
        text_content = f"""
                Hello {first_name},

                Welcome to {BRAND_NAME}! Please verify your email address to complete your registration.

                Click the link below to verify your email:
                {verification_url}

                If you didn't create an account with us, please ignore this email.

                Best regards,
                {BRAND_NAME} Team

                {PLATFORM_ATTRIBUTION}
                        """.strip()
                        
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Verify Your Email</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; background-color: #f9f9f9; }}
                        .button {{ display: inline-block; background-color: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Welcome to {BRAND_NAME}!</h1>
                        </div>
                        <div class="content">
                            <p>Hello {first_name},</p>
                            <p>Thank you for registering with {BRAND_NAME}! To complete your registration, please verify your email address.</p>
                            <p style="text-align: center;">
                                <a href="{verification_url}" class="button">Verify Email Address</a>
                            </p>
                            <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                            <p style="word-break: break-all; color: #1976d2;">{verification_url}</p>
                            <p>If you didn't create an account with us, please ignore this email.</p>
                        </div>
                        <div class="footer">
                            <p>Best regards,<br>{BRAND_NAME} Team</p>
                            <p>{PLATFORM_ATTRIBUTION}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()
        
        return self.send_email(email, subject, text_content, html_content, reply_to)
    
    def send_password_reset_email(self, email: str, first_name: str, token: str, reply_to: str = None) -> Dict[str, Any]:
        """Send password reset email."""
        subject = f"Reset Your Password - {BRAND_NAME}"
        
        reset_url = f"{self.base_url}/#/reset-password?token={token}"
        
        text_content = f"""
            Hello {first_name},

            You requested to reset your password for your {BRAND_NAME} account.

            Click the link below to reset your password:
            {reset_url}

            This link will expire in 1 hour for security reasons.

            If you didn't request a password reset, please ignore this email.

            Best regards,
            {BRAND_NAME} Team

            {PLATFORM_ATTRIBUTION}
                    """.strip()
                    
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Reset Your Password</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #8B0000; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ display: inline-block; background-color: #8B0000; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                    .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hello {first_name},</p>
                        <p>You requested to reset your password for your {BRAND_NAME} account.</p>
                        <p style="text-align: center;">
                            <a href="{reset_url}" class="button">Reset Password</a>
                        </p>
                        <div class="warning">
                            <strong>Security Notice:</strong> This link will expire in 1 hour for security reasons.
                        </div>
                        <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; color: #8B0000;">{reset_url}</p>
                        <p>If you didn't request a password reset, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>Best regards,<br>{BRAND_NAME} Team</p>
                        <p>{PLATFORM_ATTRIBUTION}</p>
                    </div>
                </div>
            </body>
            </html>
                """.strip()
        
        return self.send_email(email, subject, text_content, html_content, reply_to)
    
    def send_contact_email(self, name: str, email: str, phone: str, subject: str, message: str, reply_to: str = None) -> bool:
        """Send contact form email to the Uzima Prints support address."""
        email_subject = f"Contact Form: {subject}"

        # Escape user-supplied values before inserting into HTML to prevent XSS.
        safe_name = html_escape(name)
        safe_email = html_escape(email)
        safe_phone = html_escape(phone or 'Not provided')
        safe_subject = html_escape(subject)
        safe_message = html_escape(message)

        text_content = f"""
            New contact form submission from the {BRAND_NAME} website:

            Name: {name}
            Email: {email}
            Phone: {phone or 'Not provided'}
            Subject: {subject}

            Message:
            {message}

            ---
            This message was sent from the {BRAND_NAME} contact form.
                    """.strip()

        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Contact Form Submission</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .field {{ margin-bottom: 15px; }}
                    .label {{ font-weight: bold; color: #1976d2; }}
                    .message {{ background-color: white; padding: 15px; border-left: 4px solid #1976d2; margin: 15px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>New Contact Form Submission</h1>
                    </div>
                    <div class="content">
                        <div class="field">
                            <span class="label">Name:</span> {safe_name}
                        </div>
                        <div class="field">
                            <span class="label">Email:</span> {safe_email}
                        </div>
                        <div class="field">
                            <span class="label">Phone:</span> {safe_phone}
                        </div>
                        <div class="field">
                            <span class="label">Subject:</span> {safe_subject}
                        </div>
                        <div class="field">
                            <span class="label">Message:</span>
                            <div class="message">{safe_message}</div>
                        </div>
                    </div>
                    <div class="footer">
                        <p>This message was sent from the {BRAND_NAME} contact form.</p>
                    </div>
                </div>
            </body>
            </html>
            """.strip()
        
        result = self.send_email(
            to_email=self.client.get_from_email(),
            subject=email_subject,
            text_content=text_content,
            html_content=html_content,
            reply_to=reply_to or email  # Use provided reply_to or customer's email
        )
        
        if result.get('success'):
            # Send confirmation to customer
            self._send_contact_confirmation(name, email, subject, reply_to)
            return True
        else:
            logger.error(f"Failed to send contact email: {result.get('error')}")
            return False
    
    def _send_contact_confirmation(self, name: str, email: str, subject: str, reply_to: str = None):
        """Send confirmation email to customer."""
        confirmation_subject = f"Message Received - {BRAND_NAME}"
        
        text_content = f"""
            Hello {name},

            Thank you for contacting {BRAND_NAME}! We have received your message regarding "{subject}".

            Our team will review your message and get back to you as soon as possible.

            Best regards,
            {BRAND_NAME} Team

            Email: {INTENDED_SENDER_ADDRESS}
            {PLATFORM_ATTRIBUTION}
                    """.strip()
                    
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Message Received</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                    .contact-info {{ background-color: white; padding: 15px; border-radius: 4px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Message Received!</h1>
                    </div>
                    <div class="content">
                        <p>Hello {name},</p>
                        <p>Thank you for contacting {BRAND_NAME}! We have received your message regarding <strong>"{subject}"</strong>.</p>
                        <p>Our team will review your message and get back to you as soon as possible.</p>
                        <div class="contact-info">
                            <h3>{BRAND_NAME}</h3>
                            <p>Email: {INTENDED_SENDER_ADDRESS}</p>
                        </div>
                    </div>
                    <div class="footer">
                        <p>Best regards,<br>{BRAND_NAME} Team</p>
                        <p>{PLATFORM_ATTRIBUTION}</p>
                    </div>
                </div>
            </body>
            </html>
            """.strip()
        
        self.send_email(
            to_email=email,
            subject=confirmation_subject,
            text_content=text_content,
            html_content=html_content,
            reply_to=reply_to
        )
