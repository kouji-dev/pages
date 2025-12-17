import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'lib-list-item-row',
  imports: [CommonModule],
  template: `
    <div class="list-item-row">
      <ng-content />
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .list-item-row {
        @apply flex items-center gap-3;
        @apply px-2 py-2;
        @apply rounded-md;
        @apply text-sm;
        @apply text-navigation-foreground;
        @apply transition-colors;
        @apply w-full text-left;
        @apply h-full;
        @apply cursor-pointer;
        @apply hover:bg-navigation-accent hover:text-navigation-accent-foreground;
      }

      /* Active state */
      :host-context(.list-item--active) .list-item-row {
        @apply bg-navigation-accent text-navigation-accent-foreground font-medium;
      }

      /* Disabled state */
      :host-context(.list-item--disabled) .list-item-row {
        @apply opacity-50 cursor-not-allowed pointer-events-none;
      }

      /* Destructive variant */
      :host-context(.list-item--destructive) .list-item-row {
        @apply text-destructive;
      }

      :host-context(.list-item--destructive:not(.list-item--disabled)) .list-item-row:hover {
        @apply bg-destructive text-destructive-foreground;
      }

      /* Ensure label takes available space and actions are pushed right */
      .list-item-row ::ng-deep lib-list-item-label,
      .list-item-row ::ng-deep .list-item-label {
        @apply flex-1;
      }

      .list-item-row ::ng-deep lib-list-item-actions {
        @apply ml-auto;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListItemRow {}
