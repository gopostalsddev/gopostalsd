import os
import logging
from typing import Dict, Any, Optional
from mailersend import MailerSendClient, EmailBuilder

logger = logging.getLogger(__name__)


class MailerSendAdapter:
    """Wrapper class for MailerSend SDK that handles API key access and email sending."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize MailerSend client.

        Args:
            api_key: MailerSend API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('MAILERSEND_API_KEY')
        self.client = None
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@gopostalsd.com')
        self.from_name = os.getenv('FROM_NAME', 'Go Postal SD')

        if self.api_key:
            try:
                self.client = MailerSendClient(api_key=self.api_key)
                logger.info("MailerSend client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MailerSend client: {str(e)}")
                self.client = None
        else:
            logger.warning("MAILERSEND_API_KEY not found in environment variables")

    def send_email(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: str = None,
        reply_to: str = None,
    ) -> Dict[str, Any]:
        """
        Send email using MailerSend SDK.

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
            if not self.client:
                return {
                    'success': False,
                    'error': 'MailerSend not configured. Set MAILERSEND_API_KEY environment variable.',
                    'recipient': to_email,
                }

            reply_to_email = reply_to or self.from_email
            builder = (
                EmailBuilder()
                .from_email(self.from_email, self.from_name)
                .to(to_email)
                .subject(subject)
                .text(text_content)
                .reply_to(reply_to_email)
            )
            if html_content:
                builder = builder.html(html_content)

            response = self.client.emails.send(builder.build())

            if response.is_success:
                logger.info(f"Email sent successfully to {to_email}")
                return {
                    'success': True,
                    'message': 'Email sent successfully',
                    'status_code': response.status_code,
                    'recipient': to_email,
                    'reply_to': reply_to_email,
                }

            logger.error(f"MailerSend API error: {response.status_code}")
            return {
                'success': False,
                'error': f'MailerSend API error: {response.status_code}',
                'status_code': response.status_code,
                'recipient': to_email,
            }

        except Exception as e:
            logger.error(f"Error sending email via MailerSend: {str(e)}")
            return {
                'success': False,
                'error': f'MailerSend error: {str(e)}',
                'recipient': to_email,
            }

    @property
    def is_configured(self) -> bool:
        """Check if MailerSend is properly configured and ready to send emails."""
        return bool(self.api_key and self.client)

    def get_from_email(self) -> str:
        """Get the configured from email address."""
        return self.from_email

    def get_from_name(self) -> str:
        """Get the configured from name."""
        return self.from_name
