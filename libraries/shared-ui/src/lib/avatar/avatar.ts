import { Component, input } from '@angular/core';

export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'lib-avatar',
  template: `
    <div
      class="avatar"
      [class.avatar--xs]="size() === 'xs'"
      [class.avatar--sm]="size() === 'sm'"
      [class.avatar--md]="size() === 'md'"
      [class.avatar--lg]="size() === 'lg'"
      [class.avatar--xl]="size() === 'xl'"
      [style.background-image]="avatarUrl() ? 'url(' + avatarUrl() + ')' : null"
      [class.avatar--no-image]="!avatarUrl()"
      [title]="name()"
    >
      @if (!avatarUrl() && initials()) {
        <span class="avatar_initials">{{ initials() }}</span>
      }
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .avatar {
        @apply rounded-full;
        @apply bg-cover bg-center;
        @apply flex items-center justify-center;
        @apply flex-shrink-0;
        @apply border-2 border-white dark:border-gray-900;
        @apply box-border; /* Ensure border is included in dimensions */
      }

      /* Sizes */
      .avatar--xs {
        @apply w-6 h-6;
      }

      .avatar--sm {
        @apply w-8 h-8;
      }

      .avatar--md {
        @apply w-10 h-10;
      }

      .avatar--lg {
        @apply w-12 h-12;
      }

      .avatar--xl {
        @apply w-16 h-16;
      }

      .avatar--no-image {
        @apply bg-primary;
      }

      .avatar_initials {
        @apply text-white font-bold;
        line-height: 1; /* Center vertically */
      }

      .avatar--xs .avatar_initials {
        @apply text-xs;
      }

      .avatar--sm .avatar_initials,
      .avatar--md .avatar_initials {
        @apply text-sm;
      }

      .avatar--lg .avatar_initials {
        @apply text-base;
      }

      .avatar--xl .avatar_initials {
        @apply text-lg;
      }
    `,
  ],
})
export class Avatar {
  name = input.required<string>();
  avatarUrl = input<string>();
  initials = input<string>();
  size = input<AvatarSize>('md');
}
