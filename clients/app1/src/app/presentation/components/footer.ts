import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, IconName } from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

interface FooterLink {
  label: string;
  route: string;
}

interface SocialLink {
  name: string;
  icon: IconName;
  url: string;
  ariaLabel: string;
}

@Component({
  selector: 'app-footer',
  imports: [RouterLink, Icon, TranslatePipe],
  template: `
    <footer class="footer">
      <div class="footer_container">
        <div class="footer_content">
          <!-- Brand Section -->
          <div class="footer_section">
            <div class="footer_brand">
              <lib-icon name="file-text" size="lg" />
              <span class="footer_brand-text">Pages</span>
            </div>
            <p class="footer_description">
              {{ 'public.description' | translate }}
            </p>
          </div>

          <!-- Product Links -->
          <div class="footer_section">
            <h3 class="footer_section-title">{{ 'public.product' | translate }}</h3>
            <ul class="footer_links">
              @for (link of productLinks(); track link.route) {
                <li>
                  <a [routerLink]="[link.route]" class="footer_link">{{ link.label }}</a>
                </li>
              }
            </ul>
          </div>

          <!-- Legal Links -->
          <div class="footer_section">
            <h3 class="footer_section-title">{{ 'public.legal' | translate }}</h3>
            <ul class="footer_links">
              @for (link of legalLinks(); track link.route) {
                <li>
                  <a [routerLink]="[link.route]" class="footer_link">{{ link.label }}</a>
                </li>
              }
            </ul>
          </div>

          <!-- Contact Section -->
          <div class="footer_section">
            <h3 class="footer_section-title">{{ 'public.contact' | translate }}</h3>
            <div class="footer_contact">
              <p class="footer_contact-item">
                <lib-icon name="mail" size="sm" />
                <a href="mailto:support@pages.com" class="footer_link">support@pages.com</a>
              </p>
            </div>
            <div class="footer_social">
              @for (social of socialLinks(); track social.name) {
                <a
                  [href]="social.url"
                  [attr.aria-label]="social.ariaLabel"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="footer_social-link"
                >
                  <lib-icon [name]="social.icon" size="md" />
                </a>
              }
            </div>
          </div>
        </div>

        <!-- Copyright -->
        <div class="footer_copyright">
          <p class="footer_copyright-text">
            {{ 'public.copyright' | translate: { year: currentYear } }}
          </p>
        </div>
      </div>
    </footer>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .footer {
        @apply w-full;
        @apply border-t;
        @apply border-border;
        @apply bg-background;
        @apply mt-auto;
      }

      .footer_container {
        @apply max-w-7xl mx-auto;
        @apply px-4 sm:px-6 lg:px-8;
        @apply py-12;
      }

      .footer_content {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12;
        @apply mb-8;
      }

      .footer_section {
        @apply flex flex-col;
        @apply gap-4;
      }

      .footer_brand {
        @apply flex items-center gap-2;
        @apply font-bold text-lg;
        @apply text-foreground;
        @apply mb-2;
      }

      .footer_brand-text {
        @apply hidden sm:inline;
      }

      .footer_description {
        @apply text-sm leading-relaxed;
        @apply text-muted-foreground;
        margin: 0;
      }

      .footer_section-title {
        @apply text-base font-semibold;
        @apply text-foreground;
        margin: 0;
        @apply mb-2;
      }

      .footer_links {
        @apply flex flex-col gap-2;
        list-style: none;
        margin: 0;
        padding: 0;
      }

      .footer_link {
        @apply text-sm;
        @apply text-muted-foreground;
        text-decoration: none;
        @apply transition-colors;
        @apply hover:opacity-80;
      }

      .footer_link:hover {
        @apply text-primary;
      }

      .footer_contact {
        @apply flex flex-col gap-3;
      }

      .footer_contact-item {
        @apply flex items-center gap-2;
        @apply text-sm;
        @apply text-muted-foreground;
        margin: 0;
      }

      .footer_social {
        @apply flex items-center gap-3;
        @apply mt-4;
      }

      .footer_social-link {
        @apply flex items-center justify-center;
        @apply w-10 h-10;
        @apply rounded-lg;
        @apply text-muted-foreground;
        @apply bg-muted;
        @apply hover:bg-gray-200 transition-colors;
        text-decoration: none;
      }

      .footer_copyright {
        @apply pt-8;
        @apply border-t;
        @apply border-border;
      }

      .footer_copyright-text {
        @apply text-sm text-center;
        @apply text-muted-foreground;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Footer {
  private readonly translateService = inject(TranslateService);
  readonly currentYear = new Date().getFullYear();

  readonly productLinks = computed<FooterLink[]>(() => [
    { label: this.translateService.instant('public.features'), route: '/features' },
    { label: this.translateService.instant('public.pricing'), route: '/pricing' },
    { label: this.translateService.instant('public.documentation'), route: '/docs' },
  ]);

  readonly legalLinks = computed<FooterLink[]>(() => [
    { label: this.translateService.instant('public.termsOfService'), route: '/terms' },
    { label: this.translateService.instant('public.privacyPolicy'), route: '/privacy' },
  ]);

  readonly socialLinks = computed<SocialLink[]>(() => [
    {
      name: 'Twitter',
      icon: 'twitter',
      url: 'https://twitter.com',
      ariaLabel: this.translateService.instant('public.followTwitter'),
    },
    {
      name: 'GitHub',
      icon: 'github',
      url: 'https://github.com',
      ariaLabel: this.translateService.instant('public.visitGitHub'),
    },
    {
      name: 'LinkedIn',
      icon: 'linkedin',
      url: 'https://linkedin.com',
      ariaLabel: this.translateService.instant('public.connectLinkedIn'),
    },
  ]);
}
