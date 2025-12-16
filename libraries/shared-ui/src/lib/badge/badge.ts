import { Component, input } from '@angular/core';

export type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
export type BadgeSize = 'sm' | 'md' | 'lg';

@Component({
  selector: 'lib-badge',
  template: `
    <span
      class="badge"
      [class.badge--default]="variant() === 'default'"
      [class.badge--primary]="variant() === 'primary'"
      [class.badge--success]="variant() === 'success'"
      [class.badge--warning]="variant() === 'warning'"
      [class.badge--danger]="variant() === 'danger'"
      [class.badge--info]="variant() === 'info'"
      [class.badge--sm]="size() === 'sm'"
      [class.badge--md]="size() === 'md'"
      [class.badge--lg]="size() === 'lg'"
    >
      <ng-content></ng-content>
    </span>
  `,
  styles: [
    `
      @reference "#theme";

      .badge {
        @apply inline-flex items-center justify-center;
        @apply px-2.5 py-1 rounded-md;
        @apply text-xs font-medium;
        @apply transition-colors;
        @apply border;
      }

      /* Sizes */
      .badge--sm {
        @apply px-2 py-0.5 text-xs;
      }

      .badge--md {
        @apply px-2.5 py-1 text-xs;
      }

      .badge--lg {
        @apply px-3 py-1.5 text-sm;
      }

      /* Variants */
      .badge--default {
        @apply bg-secondary text-secondary-foreground border-border;
      }

      .badge--primary {
        @apply bg-primary/10 text-primary border-primary/20;
      }

      .badge--success {
        @apply bg-success/10 text-success border-success/20;
      }

      .badge--warning {
        @apply bg-warning/10 text-warning border-warning/20;
      }

      .badge--danger {
        @apply bg-destructive/10 text-destructive border-destructive/20;
      }

      .badge--info {
        @apply bg-info/10 text-info border-info/20;
      }
    `,
  ],
})
export class Badge {
  variant = input<BadgeVariant>('default');
  size = input<BadgeSize>('md');
}
