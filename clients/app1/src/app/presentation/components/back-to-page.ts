import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon } from 'shared-ui';

@Component({
  selector: 'app-back-to-page',
  standalone: true,
  imports: [Icon, RouterLink],
  template: `
    @if (route(); as routeValue) {
      <a [routerLink]="routeValue" class="back-to-page" [attr.aria-label]="ariaLabel() || label()">
        <lib-icon name="arrow-left" size="sm" />
        <span>{{ label() }}</span>
      </a>
    } @else {
      <a class="back-to-page" (click)="handleClick()" [attr.aria-label]="ariaLabel() || label()">
        <lib-icon name="arrow-left" size="sm" />
        <span>{{ label() }}</span>
      </a>
    }
  `,
  styles: [
    `
      @reference "#mainstyles";

      .back-to-page {
        @apply flex items-center gap-2;
        @apply mb-4;
        @apply text-sm;
        @apply text-text-secondary;
        @apply hover:text-text-primary;
        @apply transition-colors;
        @apply cursor-pointer;
        text-decoration: none;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BackToPage {
  readonly label = input.required<string>();
  readonly route = input<string | string[] | null>(null);
  readonly ariaLabel = input<string | null>(null);
  readonly onClick = output<void>();

  handleClick(): void {
    this.onClick.emit();
  }
}
