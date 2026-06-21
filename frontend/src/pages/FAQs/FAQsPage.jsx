import React from 'react';
import InformationalPageLayout from '../../components/InformationalPageLayout';

const FAQsPage = () => {
  return (
    <InformationalPageLayout
      eyebrow="Common questions"
      title="Answers to the questions customers ask before they order"
      subtitle="This page gives customers the practical details they usually need before placing a print order or contacting the shop for custom help."
      primaryAction={{ label: 'Browse products', to: '/shop' }}
      secondaryAction={{ label: 'Contact us', to: '/contact' }}
      sections={[
        {
          heading: 'How does ordering work?',
          body: 'Browse the shop, choose a product category, configure the available options, add the item to your cart, and complete checkout with shipping and payment details.',
        },
        {
          heading: 'Can I track my order after checkout?',
          body: 'Yes. Signed-in customers can use the order tracking page to review status updates, tracking numbers, and shipping destination details once fulfillment data is available.',
        },
        {
          heading: 'What if I need help choosing a product?',
          body: 'Use the contact page if you need help comparing quantities, formats, or turnaround considerations. Complex or business-critical orders are better handled with direct communication first.',
        },
        {
          heading: 'Are shipping costs included in product prices?',
          body: 'Shipping is calculated as part of the cart and checkout flow. Final totals reflect the product subtotal, shipping cost, and any tax applied to the order.',
        },
        {
          heading: 'Can I reorder something I bought before?',
          body: 'Yes. The account page shows recent orders so customers can quickly review past purchases and return to the storefront to place similar orders again.',
        },
        {
          heading: 'What if there is a problem with my order?',
          body: 'Contact the store directly with your order number. The team can review fulfillment status, shipping information, and any production issues that need follow-up.',
        },
      ]}
    />
  );
};

export default FAQsPage;
