import React from 'react';
import InformationalPageLayout from '../../components/InformationalPageLayout';

const ServicesPage = () => {
  return (
    <InformationalPageLayout
      eyebrow="What we offer"
      title="Printing, packing, and shipping built around local businesses"
      subtitle="Go Postal SD combines storefront service with online ordering so customers can move from quote to fulfillment without losing the human support that complex print jobs often need."
      primaryAction={{ label: 'Start shopping', to: '/shop' }}
      secondaryAction={{ label: 'Talk to our team', to: '/contact' }}
      metrics={[
        {
          label: 'Storefront + online',
          value: '2-speed',
          caption: 'Customers can self-serve online or move the job into direct support.',
        },
        {
          label: 'Order visibility',
          value: 'End-to-end',
          caption: 'From configured product choices through payment and tracking updates.',
        },
        {
          label: 'Best fit',
          value: 'SMBs',
          caption: 'Designed for local teams that need repeatable print operations, not one-off novelty.',
        },
        {
          label: 'Workflow style',
          value: 'Hands-on',
          caption: 'Customers get automation where it helps and people where it matters.',
        },
      ]}
      highlights={[
        {
          title: 'Commercial print products',
          description: 'Business cards, flyers, postcards, brochures, banners, and other catalog items sourced through our production partners.',
        },
        {
          title: 'Packing and shipping support',
          description: 'In-store guidance for packaging, label handling, and outbound shipment coordination for customers who need more than a simple print order.',
        },
        {
          title: 'Hands-on order review',
          description: 'Our team can help confirm quantities, timelines, shipping choices, and production requirements before large jobs move into fulfillment.',
        },
      ]}
      sections={[
        {
          heading: 'Print services',
          body: 'The storefront is built for repeatable print ordering with live product options and pricing. Customers can browse by category and configure product details before checkout.',
          bullets: [
            'Business cards, postcards, and presentation materials',
            'Flyers, brochures, rack cards, and event collateral',
            'Posters, signage, and promotional print runs',
            'Packaging and specialty items as the vendor catalog expands',
          ],
        },
        {
          heading: 'Shipping and fulfillment',
          body: 'Shipping is treated as part of the order experience, not an afterthought. Customers get clear address capture, shipment cost handling, and post-purchase tracking data when available.',
          bullets: [
            'Domestic shipping information captured at checkout',
            'Fulfillment updates through order status changes',
            'Tracking numbers and carrier details surfaced once assigned',
            'Support for reorders and coordinated print-to-ship workflows',
          ],
        },
        {
          heading: 'For growing teams',
          body: 'Small businesses often need consistency more than novelty. The platform is set up to support repeat orders, cleaner account history, and operational visibility from an admin dashboard.',
          bullets: [
            'Repeatable product ordering for recurring campaigns',
            'Account-level order history and tracking',
            'Admin-side catalog and fulfillment management',
            'Square-backed payment processing for online checkout',
          ],
        },
        {
          heading: 'When to contact the store directly',
          body: 'Some work is better handled with a person in the loop. If you have unusual turnaround requirements, file-prep questions, or a complex shipping scenario, use the contact page before submitting payment.',
          bullets: [
            'Large or unusual print quantities',
            'Special handling or delivery timing constraints',
            'Questions about artwork setup or production specs',
            'Business accounts that need custom coordination',
          ],
        },
      ]}
    />
  );
};

export default ServicesPage;
