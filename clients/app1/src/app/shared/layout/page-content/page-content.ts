import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-page-content',
  imports: [CommonModule],
  template: `
    <div class="page-content">
      <ng-content></ng-content>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .page-content {
        @apply flex-1;
        @apply w-full;
        @apply overflow-y-auto;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageContent {}
