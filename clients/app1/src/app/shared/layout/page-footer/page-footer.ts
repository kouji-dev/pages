import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Page footer component that ensures its content is always positioned at the bottom
 * of the page content area, even when there's not enough content to fill the viewport.
 */
@Component({
  selector: 'app-page-footer',
  imports: [CommonModule],
  template: ` <ng-content /> `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply flex-shrink-0;
        @apply w-full;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageFooter {}
