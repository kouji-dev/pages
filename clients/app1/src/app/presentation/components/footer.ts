import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, IconName } from 'shared-ui';

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
  imports: [RouterLink, Icon],
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
              Your all-in-one workspace for teams. Collaborate, create, and succeed together.
            </p>
          </div>

          <!-- Product Links -->
          <div class="footer_section">
            <h3 class="footer_section-title">Product</h3>
            <ul class="footer_links">
              @for (link of productLinks; track link.route) {
                <li>
                  <a [routerLink]="[link.route]" class="footer_link">{{ link.label }}</a>
                </li>
              }
            </ul>
          </div>

          <!-- Legal Links -->
          <div class="footer_section">
            <h3 class="footer_section-title">Legal</h3>
            <ul class="footer_links">
              @for (link of legalLinks; track link.route) {
                <li>
                  <a [routerLink]="[link.route]" class="footer_link">{{ link.label }}</a>
                </li>
              }
            </ul>
          </div>

          <!-- Contact Section -->
          <div class="footer_section">
            <h3 class="footer_section-title">Contact</h3>
            <div class="footer_contact">
              <p class="footer_contact-item">
                <lib-icon name="mail" size="sm" />
                <a href="mailto:support@pages.com" class="footer_link">support@pages.com</a>
              </p>
            </div>
            <div class="footer_social">
              @for (social of socialLinks; track social.name) {
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
          <p class="footer_copyright-text">© {{ currentYear }} Pages. All rights reserved.</p>
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
        border-color: var(--color-border-default);
        background: var(--color-bg-primary);
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
        color: var(--color-text-primary);
        @apply mb-2;
      }

      .footer_brand-text {
        @apply hidden sm:inline;
      }

      .footer_description {
        @apply text-sm leading-relaxed;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .footer_section-title {
        @apply text-base font-semibold;
        color: var(--color-text-primary);
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
        color: var(--color-text-secondary);
        text-decoration: none;
        @apply transition-colors;
        @apply hover:opacity-80;
      }

      .footer_link:hover {
        color: var(--color-primary-500);
      }

      .footer_contact {
        @apply flex flex-col gap-3;
      }

      .footer_contact-item {
        @apply flex items-center gap-2;
        @apply text-sm;
        color: var(--color-text-secondary);
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
        color: var(--color-text-secondary);
        background: var(--color-bg-tertiary);
        @apply hover:bg-gray-200 transition-colors;
        text-decoration: none;
      }

      .footer_copyright {
        @apply pt-8;
        @apply border-t;
        border-color: var(--color-border-default);
      }

      .footer_copyright-text {
        @apply text-sm text-center;
        color: var(--color-text-tertiary);
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Footer {
  readonly currentYear = new Date().getFullYear();

  readonly productLinks: FooterLink[] = [
    { label: 'Features', route: '/features' },
    { label: 'Pricing', route: '/pricing' },
    { label: 'Documentation', route: '/docs' },
  ];

  readonly legalLinks: FooterLink[] = [
    { label: 'Terms of Service', route: '/terms' },
    { label: 'Privacy Policy', route: '/privacy' },
  ];

  readonly socialLinks: SocialLink[] = [
    {
      name: 'Twitter',
      icon: 'twitter',
      url: 'https://twitter.com',
      ariaLabel: 'Follow us on Twitter',
    },
    {
      name: 'GitHub',
      icon: 'github',
      url: 'https://github.com',
      ariaLabel: 'Visit our GitHub',
    },
    {
      name: 'LinkedIn',
      icon: 'linkedin',
      url: 'https://linkedin.com',
      ariaLabel: 'Connect on LinkedIn',
    },
  ];
}
