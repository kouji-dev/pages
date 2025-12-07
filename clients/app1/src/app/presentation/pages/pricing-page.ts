import { Component, ChangeDetectionStrategy } from '@angular/core';
import { Button, Icon } from 'shared-ui';
import { PublicNav } from '../components/public-nav';
import { Footer } from '../components/footer';

interface PricingTier {
  name: string;
  price: string;
  priceSubtext: string;
  description: string;
  features: string[];
  ctaLabel: string;
  ctaVariant: 'primary' | 'secondary' | 'danger' | 'ghost';
  popular?: boolean;
}

interface ComparisonRow {
  feature: string;
  free: string | boolean;
  starter: string | boolean;
  professional: string | boolean;
  business: string | boolean;
  enterprise: string | boolean;
}

@Component({
  selector: 'app-pricing-page',
  imports: [Button, Icon, PublicNav, Footer],
  template: `
    <div class="pricing-page">
      <app-public-nav />
      <!-- Header Section -->
      <section class="pricing-page_header">
        <div class="pricing-page_header-container">
          <h1 class="pricing-page_title">Simple, Transparent Pricing</h1>
          <p class="pricing-page_subtitle">
            Choose the perfect plan for your team. All plans include a 14-day free trial.
          </p>
          <div class="pricing-page_toggle">
            <span class="pricing-page_toggle-label">Monthly</span>
            <span class="pricing-page_toggle-label pricing-page_toggle-label--active">Annual</span>
            <span class="pricing-page_toggle-badge">Save 20%</span>
          </div>
        </div>
      </section>

      <!-- Pricing Tiers -->
      <section class="pricing-page_content">
        <div class="pricing-page_container">
          <div class="pricing-page_grid">
            @for (tier of pricingTiers; track tier.name) {
              <div class="pricing-page_tier" [class.pricing-page_tier--popular]="tier.popular">
                @if (tier.popular) {
                  <div class="pricing-page_tier-badge">Most Popular</div>
                }
                <div class="pricing-page_tier-header">
                  <h3 class="pricing-page_tier-name">{{ tier.name }}</h3>
                  <div class="pricing-page_tier-price">
                    <span class="pricing-page_tier-price-amount">{{ tier.price }}</span>
                    <span class="pricing-page_tier-price-subtext">{{ tier.priceSubtext }}</span>
                  </div>
                  <p class="pricing-page_tier-description">{{ tier.description }}</p>
                </div>
                <div class="pricing-page_tier-content">
                  <ul class="pricing-page_tier-features">
                    @for (feature of tier.features; track feature) {
                      <li class="pricing-page_tier-feature">
                        <lib-icon name="check" size="sm" color="success" />
                        <span>{{ feature }}</span>
                      </li>
                    }
                  </ul>
                  <div class="pricing-page_tier-cta">
                    <lib-button
                      [variant]="tier.ctaVariant"
                      size="lg"
                      [link]="tier.name === 'Enterprise' ? null : ['/register']"
                      class="pricing-page_tier-button"
                    >
                      {{ tier.ctaLabel }}
                    </lib-button>
                  </div>
                </div>
              </div>
            }
          </div>
        </div>
      </section>

      <!-- Feature Comparison Table -->
      <section class="pricing-page_comparison">
        <div class="pricing-page_container">
          <div class="pricing-page_comparison-header">
            <h2 class="pricing-page_comparison-title">Compare Plans</h2>
            <p class="pricing-page_comparison-description">See how features differ across plans</p>
          </div>
          <div class="pricing-page_comparison-table">
            <table class="pricing-page_table">
              <thead>
                <tr>
                  <th>Feature</th>
                  @for (tier of pricingTiers; track tier.name) {
                    <th>{{ tier.name }}</th>
                  }
                </tr>
              </thead>
              <tbody>
                @for (row of comparisonRows; track row.feature) {
                  <tr>
                    <td class="pricing-page_table-feature">{{ row.feature }}</td>
                    <td class="pricing-page_table-value">
                      @if (isStringValue(row.free)) {
                        {{ row.free }}
                      } @else if (row.free === true) {
                        <lib-icon name="check" size="sm" color="success" />
                      } @else {
                        <lib-icon name="x" size="sm" color="text-tertiary" />
                      }
                    </td>
                    <td class="pricing-page_table-value">
                      @if (isStringValue(row.starter)) {
                        {{ row.starter }}
                      } @else if (row.starter === true) {
                        <lib-icon name="check" size="sm" color="success" />
                      } @else {
                        <lib-icon name="x" size="sm" color="text-tertiary" />
                      }
                    </td>
                    <td class="pricing-page_table-value">
                      @if (isStringValue(row.professional)) {
                        {{ row.professional }}
                      } @else if (row.professional === true) {
                        <lib-icon name="check" size="sm" color="success" />
                      } @else {
                        <lib-icon name="x" size="sm" color="text-tertiary" />
                      }
                    </td>
                    <td class="pricing-page_table-value">
                      @if (isStringValue(row.business)) {
                        {{ row.business }}
                      } @else if (row.business === true) {
                        <lib-icon name="check" size="sm" color="success" />
                      } @else {
                        <lib-icon name="x" size="sm" color="text-tertiary" />
                      }
                    </td>
                    <td class="pricing-page_table-value">
                      @if (isStringValue(row.enterprise)) {
                        {{ row.enterprise }}
                      } @else if (row.enterprise === true) {
                        <lib-icon name="check" size="sm" color="success" />
                      } @else {
                        <lib-icon name="x" size="sm" color="text-tertiary" />
                      }
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- FAQ Section -->
      <section class="pricing-page_faq">
        <div class="pricing-page_container">
          <div class="pricing-page_faq-header">
            <h2 class="pricing-page_faq-title">Frequently Asked Questions</h2>
          </div>
          <div class="pricing-page_faq-list">
            @for (faq of faqs; track faq.question) {
              <div class="pricing-page_faq-item">
                <h3 class="pricing-page_faq-question">{{ faq.question }}</h3>
                <p class="pricing-page_faq-answer">{{ faq.answer }}</p>
              </div>
            }
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="pricing-page_cta">
        <div class="pricing-page_cta-container">
          <h2 class="pricing-page_cta-title">Still have questions?</h2>
          <p class="pricing-page_cta-description">
            Our team is here to help you find the perfect plan for your needs.
          </p>
          <div class="pricing-page_cta-actions">
            <lib-button variant="primary" size="lg">Contact Sales</lib-button>
            <lib-button variant="secondary" size="lg" [link]="['/features']"
              >View Features</lib-button
            >
          </div>
        </div>
      </section>
      <app-footer />
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .pricing-page {
        @apply min-h-screen;
        @apply flex flex-col;
        background: var(--color-bg-primary);
      }

      .pricing-page_header {
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
        background: var(--color-bg-secondary);
        border-bottom: 1px solid var(--color-border-default);
      }

      .pricing-page_header-container {
        @apply max-w-4xl mx-auto;
        @apply flex flex-col items-center;
        @apply gap-6;
        @apply text-center;
      }

      .pricing-page_title {
        @apply text-4xl sm:text-5xl md:text-6xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .pricing-page_subtitle {
        @apply text-lg sm:text-xl md:text-2xl;
        color: var(--color-text-secondary);
        margin: 0;
        @apply max-w-2xl;
      }

      .pricing-page_toggle {
        @apply flex items-center gap-2;
        @apply mt-4;
      }

      .pricing-page_toggle-label {
        @apply text-sm font-medium;
        color: var(--color-text-secondary);
      }

      .pricing-page_toggle-label--active {
        color: var(--color-primary-500);
      }

      .pricing-page_toggle-badge {
        @apply text-xs font-medium;
        @apply px-2 py-1;
        @apply rounded;
        background: var(--color-success);
        color: white;
      }

      .pricing-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .pricing-page_container {
        @apply max-w-7xl mx-auto;
      }

      .pricing-page_grid {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5;
        @apply gap-6 md:gap-8;
      }

      .pricing-page_tier {
        @apply relative;
        @apply flex flex-col;
        @apply p-6 md:p-8;
        @apply rounded-lg;
        background: var(--color-bg-primary);
        border: 1px solid var(--color-border-default);
        @apply transition-shadow;
        @apply hover:shadow-lg;
      }

      .pricing-page_tier--popular {
        border: 2px solid var(--color-primary-500);
        @apply shadow-lg;
      }

      .pricing-page_tier-badge {
        @apply absolute top-0 left-1/2;
        @apply transform -translate-x-1/2 -translate-y-1/2;
        @apply px-3 py-1;
        @apply text-xs font-semibold;
        @apply rounded-full;
        background: var(--color-primary-500);
        color: white;
      }

      .pricing-page_tier-header {
        @apply flex flex-col;
        @apply gap-4;
        @apply mb-6;
        @apply text-center;
      }

      .pricing-page_tier-name {
        @apply text-2xl font-bold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .pricing-page_tier-price {
        @apply flex flex-col items-center;
        @apply gap-1;
      }

      .pricing-page_tier-price-amount {
        @apply text-4xl font-bold;
        color: var(--color-text-primary);
      }

      .pricing-page_tier-price-subtext {
        @apply text-sm;
        color: var(--color-text-secondary);
      }

      .pricing-page_tier-description {
        @apply text-sm;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .pricing-page_tier-content {
        @apply flex flex-col;
        @apply gap-6;
        @apply flex-1;
      }

      .pricing-page_tier-features {
        @apply flex flex-col;
        @apply gap-3;
        margin: 0;
        padding: 0;
        list-style: none;
      }

      .pricing-page_tier-feature {
        @apply flex items-start gap-2;
        @apply text-sm;
        color: var(--color-text-secondary);
      }

      .pricing-page_tier-feature lib-icon {
        @apply flex-shrink-0;
        @apply mt-0.5;
      }

      .pricing-page_tier-feature span {
        @apply flex-1;
      }

      .pricing-page_tier-cta {
        @apply mt-auto;
      }

      .pricing-page_tier-button {
        @apply w-full;
      }

      .pricing-page_comparison {
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
        background: var(--color-bg-secondary);
        border-top: 1px solid var(--color-border-default);
        border-bottom: 1px solid var(--color-border-default);
      }

      .pricing-page_comparison-header {
        @apply text-center;
        @apply mb-12;
      }

      .pricing-page_comparison-title {
        @apply text-3xl sm:text-4xl md:text-5xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0 0 1rem 0;
      }

      .pricing-page_comparison-description {
        @apply text-lg;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .pricing-page_comparison-table {
        @apply overflow-x-auto;
      }

      .pricing-page_table {
        @apply w-full;
        @apply border-collapse;
      }

      .pricing-page_table thead {
        background: var(--color-bg-tertiary);
      }

      .pricing-page_table th {
        @apply px-4 py-3;
        @apply text-left font-semibold;
        @apply border-b;
        border-color: var(--color-border-default);
        color: var(--color-text-primary);
      }

      .pricing-page_table th:first-child {
        @apply sticky left-0;
        background: var(--color-bg-tertiary);
        z-index: 1;
      }

      .pricing-page_table tbody tr {
        @apply border-b;
        border-color: var(--color-border-default);
      }

      .pricing-page_table tbody tr:hover {
        background: var(--color-bg-tertiary);
      }

      .pricing-page_table-feature {
        @apply px-4 py-3;
        @apply font-medium;
        color: var(--color-text-primary);
      }

      .pricing-page_table-value {
        @apply px-4 py-3;
        @apply text-center;
      }

      .pricing-page_table-value lib-icon {
        @apply inline-flex;
      }

      .pricing-page_faq {
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .pricing-page_faq-header {
        @apply text-center;
        @apply mb-12;
      }

      .pricing-page_faq-title {
        @apply text-3xl sm:text-4xl md:text-5xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .pricing-page_faq-list {
        @apply max-w-3xl mx-auto;
        @apply flex flex-col;
        @apply gap-8;
      }

      .pricing-page_faq-item {
        @apply flex flex-col;
        @apply gap-2;
      }

      .pricing-page_faq-question {
        @apply text-lg font-semibold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .pricing-page_faq-answer {
        @apply text-base;
        color: var(--color-text-secondary);
        margin: 0;
        @apply leading-relaxed;
      }

      .pricing-page_cta {
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
        background: var(--color-bg-secondary);
        border-top: 1px solid var(--color-border-default);
      }

      .pricing-page_cta-container {
        @apply max-w-3xl mx-auto;
        @apply flex flex-col items-center;
        @apply gap-6;
        @apply text-center;
      }

      .pricing-page_cta-title {
        @apply text-3xl sm:text-4xl md:text-5xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .pricing-page_cta-description {
        @apply text-lg sm:text-xl;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .pricing-page_cta-actions {
        @apply flex flex-col sm:flex-row items-center justify-center;
        @apply gap-4;
        @apply mt-4;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PricingPage {
  readonly pricingTiers: PricingTier[] = [
    {
      name: 'Free',
      price: '$0',
      priceSubtext: 'Forever free',
      description: 'Perfect for small teams and personal projects',
      features: [
        'Up to 10 users',
        'Unlimited projects and issues',
        '5GB storage per workspace',
        'Core features (issues, boards, docs)',
        'Basic integrations (5 integrations)',
        'Community support',
        'Up to 10 automation rules',
        'Basic reporting',
      ],
      ctaLabel: 'Get Started',
      ctaVariant: 'secondary',
    },
    {
      name: 'Starter',
      price: '$5',
      priceSubtext: 'per user/month (annual)',
      description: 'For growing teams that need more',
      features: [
        'Up to 25 users',
        '25GB storage per workspace',
        'All integrations',
        'API access',
        '50 automation rules',
        'Advanced reporting',
        'Email support (48-hour response)',
        'Custom fields (10 per project)',
        'Advanced permissions',
        'Export data',
      ],
      ctaLabel: 'Start Free Trial',
      ctaVariant: 'secondary',
    },
    {
      name: 'Professional',
      price: '$10',
      priceSubtext: 'per user/month (annual)',
      description: 'For established teams needing advanced features',
      features: [
        'Up to 100 users',
        '100GB storage per workspace',
        'Unlimited automation rules',
        'Advanced analytics',
        'Custom workflows',
        'Priority email support (24-hour)',
        'SSO (SAML, OAuth)',
        'Unlimited custom fields',
        'Advanced security',
        'Audit logs (90 days)',
        'White-labeling',
        'Custom domain',
        'Time tracking',
        'Client portals (1 portal)',
      ],
      ctaLabel: 'Start Free Trial',
      ctaVariant: 'primary',
      popular: true,
    },
    {
      name: 'Business',
      price: '$20',
      priceSubtext: 'per user/month (annual)',
      description: 'For large organizations with complex needs',
      features: [
        'Up to 500 users',
        '500GB storage per workspace',
        'AI-powered features',
        'Portfolio management',
        'Advanced BI and reporting',
        'Phone and chat support (4-hour)',
        'Dedicated account manager',
        'Extended audit logs (1 year)',
        'Advanced compliance',
        'Data residency options',
        'Multiple client portals',
        'Custom integrations support',
        'Training sessions',
      ],
      ctaLabel: 'Start Free Trial',
      ctaVariant: 'secondary',
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      priceSubtext: 'Contact sales',
      description: 'For enterprises with custom requirements',
      features: [
        'Unlimited users',
        'Unlimited storage',
        'Everything in Business tier',
        'Dedicated infrastructure (optional)',
        'On-premises deployment',
        '99.99% SLA',
        '24/7 phone support (1-hour)',
        'Dedicated success manager',
        'Custom SLA',
        'Advanced security audits',
        'Compliance certifications',
        'Custom integrations development',
        'White-glove migration',
      ],
      ctaLabel: 'Contact Sales',
      ctaVariant: 'primary',
    },
  ];

  readonly comparisonRows: ComparisonRow[] = [
    {
      feature: 'Users',
      free: 'Up to 10',
      starter: 'Up to 25',
      professional: 'Up to 100',
      business: 'Up to 500',
      enterprise: 'Unlimited',
    },
    {
      feature: 'Storage per workspace',
      free: '5GB',
      starter: '25GB',
      professional: '100GB',
      business: '500GB',
      enterprise: 'Unlimited',
    },
    {
      feature: 'API Access',
      free: false,
      starter: true,
      professional: true,
      business: true,
      enterprise: true,
    },
    {
      feature: 'SSO',
      free: false,
      starter: false,
      professional: true,
      business: true,
      enterprise: true,
    },
    {
      feature: 'Advanced Analytics',
      free: false,
      starter: false,
      professional: true,
      business: true,
      enterprise: true,
    },
    {
      feature: 'AI Features',
      free: false,
      starter: false,
      professional: false,
      business: true,
      enterprise: true,
    },
    {
      feature: 'Dedicated Support',
      free: false,
      starter: false,
      professional: false,
      business: true,
      enterprise: true,
    },
    {
      feature: 'On-Premises',
      free: false,
      starter: false,
      professional: false,
      business: false,
      enterprise: true,
    },
  ];

  readonly faqs = [
    {
      question: 'Can I change plans later?',
      answer:
        'Yes! You can upgrade, downgrade, or cancel your plan at any time. Changes will be reflected in your next billing cycle.',
    },
    {
      question: 'Do you offer discounts for annual billing?',
      answer:
        'Yes! Annual plans save you 20% compared to monthly billing. This discount is automatically applied when you choose annual billing.',
    },
    {
      question: 'What payment methods do you accept?',
      answer:
        'We accept all major credit cards (Visa, Mastercard, American Express) and support payments via bank transfer for Enterprise plans.',
    },
    {
      question: 'Is there a free trial?',
      answer:
        'Yes! All paid plans include a 14-day free trial. No credit card required. You can explore all features risk-free.',
    },
    {
      question: 'Can I get a refund?',
      answer:
        "We offer a 30-day money-back guarantee for all annual plans. If you're not satisfied, contact us within 30 days for a full refund.",
    },
    {
      question: 'What happens if I exceed my plan limits?',
      answer:
        "We'll notify you when you approach your limits. You can upgrade your plan at any time to continue using Pages without interruption.",
    },
  ];

  isStringValue(value: string | boolean): value is string {
    return typeof value === 'string' && value !== '';
  }
}
