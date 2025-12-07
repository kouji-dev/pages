import { Component, input, output, ChangeDetectionStrategy } from '@angular/core';
import { Button } from '../button/button';
import { Icon, IconName } from '../icon/icon';

@Component({
  selector: 'lib-empty-state',
  imports: [Button, Icon],
  template: `
    <div class="empty-state">
      <div class="empty-state_content">
        @if (icon()) {
          <lib-icon
            [name]="icon()!"
            size="xl"
            [color]="'text-tertiary'"
            [ariaLabel]="iconLabel() || 'Empty state'"
          />
        }
        <h3 class="empty-state_title">{{ title() || 'No items found' }}</h3>
        @if (message()) {
          <p class="empty-state_message">{{ message() }}</p>
        }
        @if (actionLabel()) {
          <lib-button
            [variant]="actionVariant()"
            [leftIcon]="actionIcon() || null"
            (clicked)="onAction.emit()"
            class="empty-state_button"
          >
            {{ actionLabel() }}
          </lib-button>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .empty-state {
        @apply flex flex-col items-center justify-center;
        @apply w-full h-full;
        @apply py-12 px-4;
        min-height: 200px;
      }

      .empty-state_content {
        @apply flex flex-col items-center justify-center;
        @apply gap-3;
        @apply text-center;
        @apply w-full;
        max-width: 400px;
      }

      .empty-state_button {
        @apply mt-4;
      }

      .empty-state_title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .empty-state_message {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EmptyState {
  title = input<string>('');
  message = input<string>('');
  icon = input<IconName | undefined>(undefined);
  iconLabel = input<string>('');
  actionLabel = input<string>('');
  actionIcon = input<IconName | undefined>(undefined);
  actionVariant = input<'primary' | 'secondary' | 'danger' | 'ghost'>('primary');

  onAction = output<void>();
}
