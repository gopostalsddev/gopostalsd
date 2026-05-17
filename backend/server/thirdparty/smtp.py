import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SMTPAdapter:
    """SMTP email client that handles SMTP configuration and email sending."""
    
    def __init__(self, 
                 smtp_server: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 use_tls: Optional[bool] = None,
                 from_email: Optional[str] = None,
                 from_name: Optional[str] = None):
        """
        Initialize SMTP client.
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Whether to use TLS encryption
            from_email: From email address
            from_name: From name
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.use_tls = use_tls if use_tls is not None else os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        self.from_email = from_email or os.getenv('FROM_EMAIL', 'noreply@gopostalsd.com')
        self.from_name = from_name or os.getenv('FROM_NAME', 'Go Postal SD')
        
        # Validate configuration
        self._is_configured = bool(self.username and self.password)
        
        if not self._is_configured:
            logger.warning("SMTP not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
        else:
            logger.info(f"SMTP client configured for {self.smtp_server}:{self.smtp_port}")
    
    def send_email(self, to_email: str, subject: str, text_content: str, html_content: str = None, reply_to: str = None) -> Dict[str, Any]:
        """
        Send email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            text_content: Plain text content
            html_content: HTML content (optional)
            reply_to: Reply-to email address (optional, defaults to from_email)
        
        Returns:
            Dict containing send result with success status and details
        """
        try:
            if not self._is_configured:
                return {
                    'success': False, 
                    'error': 'SMTP not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.',
                    'recipient': to_email
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add reply-to (defaults to from_email if not provided)
            reply_to_email = reply_to or self.from_email
            msg['Reply-To'] = reply_to_email
            
            # Add text content
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML content if provided
            if html_content:
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.username, self.password)
                
                # Send email
                text = msg.as_string()
                server.sendmail(self.from_email, to_email, text)
                
                logger.info(f"Email sent successfully via SMTP to {to_email}")
                return {
                    'success': True,
                    'message': 'Email sent successfully via SMTP',
                    'recipient': to_email,
                    'provider': 'SMTP',
                    'reply_to': reply_to_email
                }
                
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return {
                'success': False,
                'error': f'SMTP authentication failed: {str(e)}',
                'recipient': to_email,
                'provider': 'SMTP'
            }
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return {
                'success': False,
                'error': f'SMTP error: {str(e)}',
                'recipient': to_email,
                'provider': 'SMTP'
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email via SMTP: {str(e)}")
            return {
                'success': False,
                'error': f'SMTP error: {str(e)}',
                'recipient': to_email,
                'provider': 'SMTP'
            }
    
    @property
    def is_configured(self) -> bool:
        """Check if SMTP is properly configured and ready to send emails."""
        return self._is_configured
    
    def get_from_email(self) -> str:
        """Get the configured from email address."""
        return self.from_email
    
    def get_from_name(self) -> str:
        """Get the configured from name."""
        return self.from_name
    
    def get_smtp_info(self) -> Dict[str, Any]:
        """Get SMTP configuration info (without sensitive data)."""
        return {
            'server': self.smtp_server,
            'port': self.smtp_port,
            'use_tls': self.use_tls,
            'from_email': self.from_email,
            'from_name': self.from_name,
            'configured': self._is_configured
        }
