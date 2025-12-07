import { Component, ChangeDetectionStrategy } from '@angular/core';
import { Button } from 'shared-ui';

@Component({
  selector: 'app-not-found',
  imports: [Button],
  template: `
    <div class="not-found">
      <div class="not-found_content">
        <h1 class="not-found_title">404</h1>
        <p class="not-found_message">Page not found</p>
        <p class="not-found_description">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <lib-button variant="primary" [link]="['/']"> Go to Home </lib-button>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .not-found {
        @apply min-h-screen;
        @apply flex items-center justify-center;
        @apply px-4;
      }

      .not-found_content {
        @apply text-center;
        @apply max-w-md;
      }

      .not-found_title {
        @apply text-8xl font-bold;
        @apply mb-4;
        @apply text-primary-600;
      }

      .not-found_message {
        @apply text-2xl font-semibold;
        @apply mb-2;
        @apply text-text-primary;
      }

      .not-found_description {
        @apply mb-6;
        @apply text-text-secondary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NotFoundComponent {}
