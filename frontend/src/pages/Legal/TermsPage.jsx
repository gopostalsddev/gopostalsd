import React from 'react';
import InformationalPageLayout from '../../components/InformationalPageLayout';

const TermsPage = () => {
  return (
    <InformationalPageLayout
      eyebrow="Legal"
      title="Terms of service"
      subtitle="These terms govern use of the Go Postal SD website, customer accounts, online checkout, payment handling, and order fulfillment workflows for printing and shipping-related services. Effective date: June 20, 2026."
      primaryAction={{ label: 'Contact us', to: '/contact' }}
      secondaryAction={{ label: 'Privacy policy', to: '/privacy' }}
      sections={[
        {
          heading: 'Storefront and service scope',
          body: 'Go Postal SD operates this website to support product browsing, customer accounts, online ordering, payment collection, and fulfillment coordination for printing and related shipping services. Availability, pricing, and fulfillment timelines may change when vendor catalog data, shipping conditions, or operational constraints change.',
          fullWidth: true,
        },
        {
          heading: 'Orders and production approval',
          body: 'When you place an order, you are asking Go Postal SD to begin production and fulfillment based on the product options, quantities, addresses, and other information you submitted. The store may pause, reject, or request clarification on an order if artwork, product configuration, address accuracy, payment status, or fulfillment feasibility is incomplete or inconsistent. Order confirmation does not guarantee immediate production if additional review is required.',
        },
        {
          heading: 'Pricing, taxes, and payment processing',
          body: 'Displayed pricing may include catalog-driven product values, shipping charges, and taxes calculated at checkout. Payments are processed through third-party providers, including Square, and order completion depends on successful payment authorization. Go Postal SD does not guarantee that a cart total will remain unchanged if product, shipping, or tax inputs change before checkout is completed.',
          bullets: [
            'You authorize Go Postal SD and its payment providers to charge the total shown at checkout.',
            'Failed, reversed, or disputed payments may delay, suspend, or cancel order fulfillment.',
            'Refund timing depends on the payment provider and the stage of fulfillment.',
          ],
        },
        {
          heading: 'Cancellations, changes, and refunds',
          body: 'Requests to change or cancel an order must be made as quickly as possible. Cancellations, production changes, and refunds are handled case by case at Go Postal SD’s discretion. Because print and fulfillment work may begin promptly after payment, the store may decline a cancellation or refund request depending on production status, shipment status, payment status, and the reason for the request.',
          bullets: [
            'Custom and print-related orders are reviewed case by case rather than governed by an automatic cancellation guarantee.',
            'Orders already shipped are generally handled as support or exception cases rather than simple cancellations.',
            'Approved refunds are typically returned to the original payment method when provider rules allow it.',
          ],
        },
        {
          heading: 'Customer responsibilities',
          body: 'Customers are responsible for the accuracy and legality of the information they submit through the website. That includes contact information, shipping and billing addresses, requested quantities, and any design or production inputs associated with an order.',
          bullets: [
            'Review all order details before submitting payment.',
            'Provide only artwork, branding, or content you own or are authorized to use.',
            'Monitor order confirmation and fulfillment communications sent to your account email address.',
          ],
        },
        {
          heading: 'Changes, cancellations, and delivery',
          body: 'Once an order enters production or is handed off for shipment, changes may be limited or unavailable. Delivery estimates and tracking events depend on carriers and external vendors. Go Postal SD is not responsible for delays caused by customer-supplied errors, carrier disruptions, force majeure events, or third-party provider outages outside the store’s reasonable control. For shipping issues, the store may review damaged-order claims, but replacements, credits, or other resolutions remain subject to review.',
        },
        {
          heading: 'Support and disputes',
          body: 'If there is a problem with an order, contact Go Postal SD promptly and include the order number when available. The store may request supporting information before issuing a replacement, adjustment, or refund decision.',
          bullets: [
            'Go Postal SD, 1501 India St Suite 103, San Diego, CA 92101',
            'Phone: (619) 237-0374',
            'Email: gopostalsd@gmail.com',
          ],
        },
      ]}
    />
  );
};

export default TermsPage;
