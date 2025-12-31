import { Component, ChangeDetectionStrategy, input, booleanAttribute } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-page-content',
  imports: [CommonModule],
  template: ` <ng-content /> `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply flex-1;
        @apply w-full;
        @apply h-full;
        @apply overflow-y-auto;
        @apply min-h-0;
        @apply flex flex-col;
      }

      :host:not(.page-content--no-padding) {
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      :host.page-content--no-padding {
        @apply p-0;
      }
    `,
  ],
  host: {
    '[class.page-content--no-padding]': 'noPadding()',
  },
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageContent {
  noPadding = input(false, { transform: booleanAttribute });
}
