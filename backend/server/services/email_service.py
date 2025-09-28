"""
Email Service for Go Postal SD Application

This module handles email sending for authentication, notifications, and other purposes.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from server.config import DevelopmentConfig, TestingConfig, ProductionConfig
import os

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails.
    """

    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@gopostalsd.com')
        self.from_name = os.getenv('FROM_NAME', 'Go Postal SD')
        self.base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    def send_verification_email(self, email: str, first_name: str, token: str) -> Dict[str, Any]:
        """
        Send email verification email.
        
        Args:
            email: Recipient email
            first_name: Recipient first name
            token: Verification token
            
        Returns:
            Dict containing send result
        """
        try:
            verification_url = f"{self.base_url}/verify-email?token={token}"
            
            subject = "Verify Your Email Address - Go Postal SD"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Email Verification</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Go Postal SD!</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {first_name},</h2>
                        <p>Thank you for registering with Go Postal SD. To complete your registration and start using our services, please verify your email address by clicking the button below:</p>
                        
                        <div style="text-align: center;">
                            <a href="{verification_url}" class="button">Verify Email Address</a>
                        </div>
                        
                        <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 5px;">{verification_url}</p>
                        
                        <p><strong>This link will expire in 24 hours.</strong></p>
                        
                        <p>If you didn't create an account with us, please ignore this email.</p>
                        
                        <p>Best regards,<br>The Go Postal SD Team</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Go Postal SD. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hi {first_name},
            
            Thank you for registering with Go Postal SD. To complete your registration and start using our services, please verify your email address by visiting the following link:
            
            {verification_url}
            
            This link will expire in 24 hours.
            
            If you didn't create an account with us, please ignore this email.
            
            Best regards,
            The Go Postal SD Team
            """
            
            return self._send_email(email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return {'success': False, 'error': str(e)}

    def send_password_reset_email(self, email: str, first_name: str, token: str) -> Dict[str, Any]:
        """
        Send password reset email.
        
        Args:
            email: Recipient email
            first_name: Recipient first name
            token: Reset token
            
        Returns:
            Dict containing send result
        """
        try:
            reset_url = f"{self.base_url}/reset-password?token={token}"
            
            subject = "Reset Your Password - Go Postal SD"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {first_name},</h2>
                        <p>We received a request to reset your password for your Go Postal SD account. If you made this request, click the button below to reset your password:</p>
                        
                        <div style="text-align: center;">
                            <a href="{reset_url}" class="button">Reset Password</a>
                        </div>
                        
                        <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 5px;">{reset_url}</p>
                        
                        <div class="warning">
                            <p><strong>Important:</strong></p>
                            <ul>
                                <li>This link will expire in 1 hour</li>
                                <li>If you didn't request this password reset, please ignore this email</li>
                                <li>Your password will not be changed until you click the link above</li>
                            </ul>
                        </div>
                        
                        <p>For security reasons, if you didn't request this password reset, please contact our support team immediately.</p>
                        
                        <p>Best regards,<br>The Go Postal SD Team</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Go Postal SD. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hi {first_name},
            
            We received a request to reset your password for your Go Postal SD account. If you made this request, visit the following link to reset your password:
            
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this password reset, please ignore this email. Your password will not be changed until you click the link above.
            
            For security reasons, if you didn't request this password reset, please contact our support team immediately.
            
            Best regards,
            The Go Postal SD Team
            """
            
            return self._send_email(email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return {'success': False, 'error': str(e)}

    def send_welcome_email(self, email: str, first_name: str) -> Dict[str, Any]:
        """
        Send welcome email after successful verification.
        
        Args:
            email: Recipient email
            first_name: Recipient first name
            
        Returns:
            Dict containing send result
        """
        try:
            subject = "Welcome to Go Postal SD!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to Go Postal SD</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Go Postal SD!</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {first_name},</h2>
                        <p>Congratulations! Your email has been verified and your account is now active. You can now start using all the features of Go Postal SD.</p>
                        
                        <h3>What you can do now:</h3>
                        <ul>
                            <li>Browse our product catalog</li>
                            <li>Get instant pricing for your projects</li>
                            <li>Place orders with confidence</li>
                            <li>Track your orders in real-time</li>
                            <li>Manage your account settings</li>
                        </ul>
                        
                        <div style="text-align: center;">
                            <a href="{self.base_url}/shop" class="button">Start Shopping</a>
                        </div>
                        
                        <p>If you have any questions or need assistance, don't hesitate to contact our support team.</p>
                        
                        <p>Thank you for choosing Go Postal SD!</p>
                        
                        <p>Best regards,<br>The Go Postal SD Team</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Go Postal SD. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hi {first_name},
            
            Congratulations! Your email has been verified and your account is now active. You can now start using all the features of Go Postal SD.
            
            What you can do now:
            - Browse our product catalog
            - Get instant pricing for your projects
            - Place orders with confidence
            - Track your orders in real-time
            - Manage your account settings
            
            Visit {self.base_url}/shop to start shopping!
            
            If you have any questions or need assistance, don't hesitate to contact our support team.
            
            Thank you for choosing Go Postal SD!
            
            Best regards,
            The Go Postal SD Team
            """
            
            return self._send_email(email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _send_email(self, to_email: str, subject: str, text_content: str, html_content: str = None) -> Dict[str, Any]:
        """
        Send email using SMTP.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            text_content: Plain text content
            html_content: HTML content (optional)
            
        Returns:
            Dict containing send result
        """
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured, skipping email send")
                return {'success': True, 'message': 'Email service not configured'}

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text content
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)

            # Add HTML content if provided
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return {'success': True, 'message': 'Email sent successfully'}

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return {'success': False, 'error': str(e)}
