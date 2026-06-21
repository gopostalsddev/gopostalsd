import React from 'react';
import InformationalPageLayout from '../../components/InformationalPageLayout';

const PrivacyPage = () => {
  return (
    <InformationalPageLayout
      eyebrow="Legal"
      title="Privacy policy"
      subtitle="This policy explains how Go Postal SD collects, uses, and shares information required to run customer accounts, payments, fulfillment, and support workflows through this website. Effective date: June 20, 2026."
      primaryAction={{ label: 'Terms of service', to: '/terms' }}
      secondaryAction={{ label: 'Contact us', to: '/contact' }}
      sections={[
        {
          heading: 'Information we collect',
          body: 'The site collects account details, contact information, shipping and billing addresses, order history, and service interaction data needed to support checkout, fulfillment, and customer support. Depending on how you use the site, this may include registration details, session-related authentication data, cart contents, and order tracking information.',
          bullets: [
            'Name, email, and account credentials',
            'Shipping and billing addresses',
            'Order history and cart activity',
            'Payment-related transaction references returned by payment providers',
          ],
        },
        {
          heading: 'How the information is used',
          body: 'Collected data is used to authenticate users, process orders, send confirmations, manage fulfillment, surface order tracking information, respond to contact requests, and support customer service workflows. Go Postal SD uses this information only to operate, secure, and improve the services provided through the website.',
          bullets: [
            'Customer information is not sold as part of ordinary business operations through this site.',
            'Marketing messages should not be sent without customer consent.',
          ],
        },
        {
          heading: 'Sharing with service providers',
          body: 'Go Postal SD may share customer information with third-party services only to the extent required to complete business operations supported by this site.',
          bullets: [
            'Square for payment processing and transaction handling',
            'MailerSend or SMTP providers for transactional emails',
            'Supabase for file storage where applicable',
            'Print and catalog vendors such as Sinalite when product or fulfillment workflows require it',
          ],
        },
        {
          heading: 'Email, payments, and order communications',
          body: 'If you create an account or place an order, Go Postal SD may send operational messages such as verification emails, password reset emails, order confirmations, and order support communications. These messages are service-related and not limited to marketing use.',
        },
        {
          heading: 'Retention and security',
          body: 'Account, order, and operational data may be retained for business records, fulfillment history, fraud prevention, support, and legal compliance. Go Postal SD uses reasonable technical and administrative safeguards, but no internet-connected system can be guaranteed perfectly secure. Payment card information is handled by payment providers rather than stored directly by the site as part of ordinary order processing.',
        },
        {
          heading: 'Your choices and contact rights',
          body: 'Customers may contact Go Postal SD for help with account access, order questions, or corrections to fulfillment-related information. Requests involving deletion, export, or legal rights handling may depend on applicable law, payment record obligations, fraud prevention needs, and fulfillment history. Where legally allowed, Go Postal SD may review requests to delete account-related information.',
          bullets: [
            'Go Postal SD, 1501 India St Suite 103, San Diego, CA 92101',
            'Phone: (619) 237-0374',
            'Email: gopostalsd@gmail.com',
            'Contact us for any issue; response times may vary and are not guaranteed.',
          ],
          fullWidth: true,
        },
      ]}
    />
  );
};

export default PrivacyPage;
