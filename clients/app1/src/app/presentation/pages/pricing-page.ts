import { Component, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { Button, Icon } from 'shared-ui';
import { PublicNav } from '../components/public-nav';
import { Footer } from '../components/footer';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

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
  imports: [Button, Icon, PublicNav, Footer, TranslatePipe],
  template: `
    <div class="pricing-page">
      <app-public-nav />
      <!-- Header Section -->
      <section class="pricing-page_header">
        <div class="pricing-page_header-container">
          <h1 class="pricing-page_title">{{ 'public.pricingPage.header.title' | translate }}</h1>
          <p class="pricing-page_subtitle">
            {{ 'public.pricingPage.header.subtitle' | translate }}
          </p>
          <div class="pricing-page_toggle">
            <span class="pricing-page_toggle-label">{{
              'public.pricingPage.header.monthly' | translate
            }}</span>
            <span class="pricing-page_toggle-label pricing-page_toggle-label--active">{{
              'public.pricingPage.header.annual' | translate
            }}</span>
            <span class="pricing-page_toggle-badge">{{
              'public.pricingPage.header.save20' | translate
            }}</span>
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
                  <div class="pricing-page_tier-badge">
                    {{ 'public.pricingPage.mostPopular' | translate }}
                  </div>
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
                      [link]="
                        tier.ctaVariant === 'primary' && tier.name === pricingTiers()[4].name
                          ? null
                          : ['/register']
                      "
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
            <h2 class="pricing-page_comparison-title">
              {{ 'public.pricingPage.comparison.title' | translate }}
            </h2>
            <p class="pricing-page_comparison-description">
              {{ 'public.pricingPage.comparison.description' | translate }}
            </p>
          </div>
          <div class="pricing-page_comparison-table">
            <table class="pricing-page_table">
              <thead>
                <tr>
                  <th>{{ 'public.pricingPage.comparison.feature' | translate }}</th>
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
            <h2 class="pricing-page_faq-title">{{ 'public.pricingPage.faq.title' | translate }}</h2>
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
          <h2 class="pricing-page_cta-title">{{ 'public.pricingPage.cta.title' | translate }}</h2>
          <p class="pricing-page_cta-description">
            {{ 'public.pricingPage.cta.description' | translate }}
          </p>
          <div class="pricing-page_cta-actions">
            <lib-button variant="primary" size="lg">{{
              'public.pricingPage.cta.contactSales' | translate
            }}</lib-button>
            <lib-button variant="secondary" size="lg" [link]="['/features']">{{
              'public.pricingPage.cta.viewFeatures' | translate
            }}</lib-button>
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
  private readonly translateService = inject(TranslateService);

  readonly pricingTiers = computed<PricingTier[]>(() => [
    {
      name: this.translateService.instant('public.pricingPage.tiers.free.name'),
      price: '$0',
      priceSubtext: this.translateService.instant('public.pricingPage.tiers.free.priceSubtext'),
      description: this.translateService.instant('public.pricingPage.tiers.free.description'),
      features: [
        this.translateService.instant('public.pricingPage.tiers.free.features.users'),
        this.translateService.instant('public.pricingPage.tiers.free.features.projects'),
        this.translateService.instant('public.pricingPage.tiers.free.features.storage'),
        this.translateService.instant('public.pricingPage.tiers.free.features.coreFeatures'),
        this.translateService.instant('public.pricingPage.tiers.free.features.integrations'),
        this.translateService.instant('public.pricingPage.tiers.free.features.support'),
        this.translateService.instant('public.pricingPage.tiers.free.features.automation'),
        this.translateService.instant('public.pricingPage.tiers.free.features.reporting'),
      ],
      ctaLabel: this.translateService.instant('public.pricingPage.getStarted'),
      ctaVariant: 'secondary',
    },
    {
      name: this.translateService.instant('public.pricingPage.tiers.starter.name'),
      price: '$5',
      priceSubtext: this.translateService.instant('public.pricingPage.tiers.starter.priceSubtext'),
      description: this.translateService.instant('public.pricingPage.tiers.starter.description'),
      features: [
        this.translateService.instant('public.pricingPage.tiers.starter.features.users'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.storage'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.integrations'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.api'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.automation'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.reporting'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.support'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.customFields'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.permissions'),
        this.translateService.instant('public.pricingPage.tiers.starter.features.export'),
      ],
      ctaLabel: this.translateService.instant('public.pricingPage.startFreeTrial'),
      ctaVariant: 'secondary',
    },
    {
      name: this.translateService.instant('public.pricingPage.tiers.professional.name'),
      price: '$10',
      priceSubtext: this.translateService.instant(
        'public.pricingPage.tiers.professional.priceSubtext',
      ),
      description: this.translateService.instant(
        'public.pricingPage.tiers.professional.description',
      ),
      features: [
        this.translateService.instant('public.pricingPage.tiers.professional.features.users'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.storage'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.automation'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.analytics'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.workflows'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.support'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.sso'),
        this.translateService.instant(
          'public.pricingPage.tiers.professional.features.customFields',
        ),
        this.translateService.instant('public.pricingPage.tiers.professional.features.security'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.audit'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.whiteLabel'),
        this.translateService.instant('public.pricingPage.tiers.professional.features.domain'),
        this.translateService.instant(
          'public.pricingPage.tiers.professional.features.timeTracking',
        ),
        this.translateService.instant('public.pricingPage.tiers.professional.features.portals'),
      ],
      ctaLabel: this.translateService.instant('public.pricingPage.startFreeTrial'),
      ctaVariant: 'primary',
      popular: true,
    },
    {
      name: this.translateService.instant('public.pricingPage.tiers.business.name'),
      price: '$20',
      priceSubtext: this.translateService.instant('public.pricingPage.tiers.business.priceSubtext'),
      description: this.translateService.instant('public.pricingPage.tiers.business.description'),
      features: [
        this.translateService.instant('public.pricingPage.tiers.business.features.users'),
        this.translateService.instant('public.pricingPage.tiers.business.features.storage'),
        this.translateService.instant('public.pricingPage.tiers.business.features.ai'),
        this.translateService.instant('public.pricingPage.tiers.business.features.portfolio'),
        this.translateService.instant('public.pricingPage.tiers.business.features.bi'),
        this.translateService.instant('public.pricingPage.tiers.business.features.support'),
        this.translateService.instant('public.pricingPage.tiers.business.features.accountManager'),
        this.translateService.instant('public.pricingPage.tiers.business.features.audit'),
        this.translateService.instant('public.pricingPage.tiers.business.features.compliance'),
        this.translateService.instant('public.pricingPage.tiers.business.features.dataResidency'),
        this.translateService.instant('public.pricingPage.tiers.business.features.portals'),
        this.translateService.instant('public.pricingPage.tiers.business.features.integrations'),
        this.translateService.instant('public.pricingPage.tiers.business.features.training'),
      ],
      ctaLabel: this.translateService.instant('public.pricingPage.startFreeTrial'),
      ctaVariant: 'secondary',
    },
    {
      name: this.translateService.instant('public.pricingPage.tiers.enterprise.name'),
      price: this.translateService.instant('public.pricingPage.tiers.enterprise.price'),
      priceSubtext: this.translateService.instant(
        'public.pricingPage.tiers.enterprise.priceSubtext',
      ),
      description: this.translateService.instant('public.pricingPage.tiers.enterprise.description'),
      features: [
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.users'),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.storage'),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.businessTier'),
        this.translateService.instant(
          'public.pricingPage.tiers.enterprise.features.infrastructure',
        ),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.onPremises'),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.sla'),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.support'),
        this.translateService.instant(
          'public.pricingPage.tiers.enterprise.features.successManager',
        ),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.customSla'),
        this.translateService.instant(
          'public.pricingPage.tiers.enterprise.features.securityAudits',
        ),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.compliance'),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.integrations'),
        this.translateService.instant('public.pricingPage.tiers.enterprise.features.migration'),
      ],
      ctaLabel: this.translateService.instant('public.pricingPage.contactSales'),
      ctaVariant: 'primary',
    },
  ]);

  readonly comparisonRows = computed<ComparisonRow[]>(() => [
    {
      feature: this.translateService.instant('public.pricingPage.comparison.rows.users.feature'),
      free: this.translateService.instant('public.pricingPage.comparison.rows.users.free'),
      starter: this.translateService.instant('public.pricingPage.comparison.rows.users.starter'),
      professional: this.translateService.instant(
        'public.pricingPage.comparison.rows.users.professional',
      ),
      business: this.translateService.instant('public.pricingPage.comparison.rows.users.business'),
      enterprise: this.translateService.instant(
        'public.pricingPage.comparison.rows.users.enterprise',
      ),
    },
    {
      feature: this.translateService.instant('public.pricingPage.comparison.rows.storage.feature'),
      free: '5GB',
      starter: '25GB',
      professional: '100GB',
      business: '500GB',
      enterprise: this.translateService.instant('public.pricingPage.unlimited'),
    },
    {
      feature: this.translateService.instant('public.pricingPage.comparison.rows.api.feature'),
      free: false,
      starter: true,
      professional: true,
      business: true,
      enterprise: true,
    },
    {
      feature: this.translateService.instant('public.pricingPage.comparison.rows.sso.feature'),
      free: false,
      starter: false,
      professional: true,
      business: true,
      enterprise: true,
    },
    {
      feature: this.translateService.instant(
        'public.pricingPage.comparison.rows.analytics.feature',
      ),
      free: false,
      starter: false,
      professional: true,
      business: true,
      enterprise: true,
    },
    {
      feature: this.translateService.instant('public.pricingPage.comparison.rows.ai.feature'),
      free: false,
      starter: false,
      professional: false,
      business: true,
      enterprise: true,
    },
    {
      feature: this.translateService.instant('public.pricingPage.comparison.rows.support.feature'),
      free: false,
      starter: false,
      professional: false,
      business: true,
      enterprise: true,
    },
    {
      feature: this.translateService.instant(
        'public.pricingPage.comparison.rows.onPremises.feature',
      ),
      free: false,
      starter: false,
      professional: false,
      business: false,
      enterprise: true,
    },
  ]);

  readonly faqs = computed(() => [
    {
      question: this.translateService.instant('public.pricingPage.faq.items.changePlans.question'),
      answer: this.translateService.instant('public.pricingPage.faq.items.changePlans.answer'),
    },
    {
      question: this.translateService.instant('public.pricingPage.faq.items.discounts.question'),
      answer: this.translateService.instant('public.pricingPage.faq.items.discounts.answer'),
    },
    {
      question: this.translateService.instant(
        'public.pricingPage.faq.items.paymentMethods.question',
      ),
      answer: this.translateService.instant('public.pricingPage.faq.items.paymentMethods.answer'),
    },
    {
      question: this.translateService.instant('public.pricingPage.faq.items.freeTrial.question'),
      answer: this.translateService.instant('public.pricingPage.faq.items.freeTrial.answer'),
    },
    {
      question: this.translateService.instant('public.pricingPage.faq.items.refund.question'),
      answer: this.translateService.instant('public.pricingPage.faq.items.refund.answer'),
    },
    {
      question: this.translateService.instant('public.pricingPage.faq.items.exceedLimits.question'),
      answer: this.translateService.instant('public.pricingPage.faq.items.exceedLimits.answer'),
    },
  ]);

  isStringValue(value: string | boolean): value is string {
    return typeof value === 'string' && value !== '';
  }

  isEnterpriseTier(tier: PricingTier): boolean {
    return tier.ctaLabel === this.translateService.instant('public.pricingPage.contactSales');
  }
}
