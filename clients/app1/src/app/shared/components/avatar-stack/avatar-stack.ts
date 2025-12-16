import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Avatar } from 'shared-ui';

export interface AvatarStackItem {
  name: string;
  avatarUrl?: string;
  initials?: string;
}

@Component({
  selector: 'app-avatar-stack',
  standalone: true,
  imports: [CommonModule, Avatar],
  template: `
    <div class="avatar-stack">
      @for (item of visibleItems(); track $index) {
        <div class="avatar-wrapper" [style.z-index]="items().length - $index">
          <lib-avatar
            [name]="item.name"
            [avatarUrl]="item.avatarUrl"
            [initials]="item.initials"
            [size]="size()"
          />
        </div>
      }

      @if (hiddenCount() > 0) {
        <div
          class="avatar-overflow"
          [class.avatar-overflow--sm]="size() === 'sm'"
          [class.avatar-overflow--xs]="size() === 'xs'"
        >
          +{{ hiddenCount() }}
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .avatar-stack {
        @apply flex items-center;
      }

      .avatar-wrapper {
        @apply -ml-2 first:ml-0;
        @apply transition-transform hover:-translate-y-0.5;
        @apply rounded-full bg-background; /* Border color match */
        padding: 1px; /* Gap effect */
      }

      .avatar-overflow {
        @apply -ml-2 relative z-0;
        @apply flex items-center justify-center;
        @apply rounded-full bg-gray-100 dark:bg-gray-800;
        @apply text-xs font-medium text-gray-500;
        @apply border-2 border-white dark:border-gray-900;
        @apply w-8 h-8; /* Default md size match */
      }

      .avatar-overflow--sm {
        @apply w-6 h-6 text-[10px];
      }

      .avatar-overflow--xs {
        @apply w-5 h-5 text-[9px];
      }
    `,
  ],
})
export class AvatarStack {
  items = input.required<AvatarStackItem[]>();
  limit = input(3);
  size = input<'xs' | 'sm' | 'md'>('sm');

  readonly visibleItems = computed(() => {
    return this.items().slice(0, this.limit());
  });

  readonly hiddenCount = computed(() => {
    return Math.max(0, this.items().length - this.limit());
  });
}
