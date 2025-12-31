import { Component, ChangeDetectionStrategy } from '@angular/core';
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
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply min-h-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageContent {}
