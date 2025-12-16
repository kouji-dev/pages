import { Component, ChangeDetectionStrategy } from '@angular/core';
import { Button } from 'shared-ui';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-not-found',
  imports: [Button, TranslatePipe],
  template: `
    <div class="not-found">
      <div class="not-found_content">
        <h1 class="not-found_title">404</h1>
        <p class="not-found_message">{{ 'common.notFound.title' | translate }}</p>
        <p class="not-found_description">
          {{ 'common.notFound.description' | translate }}
        </p>
        <lib-button variant="primary" [link]="['/']">{{
          'common.notFound.goToHome' | translate
        }}</lib-button>
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
        @apply text-primary;
      }

      .not-found_message {
        @apply text-2xl font-semibold;
        @apply mb-2;
        @apply text-foreground;
      }

      .not-found_description {
        @apply mb-6;
        @apply text-muted-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NotFoundComponent {}
