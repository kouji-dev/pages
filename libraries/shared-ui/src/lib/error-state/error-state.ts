import { Component, input, output, ChangeDetectionStrategy } from '@angular/core';
import { Button } from '../button/button';
import { Icon } from '../icon/icon';

@Component({
  selector: 'lib-error-state',
  imports: [Button, Icon],
  template: `
    <div class="error-state">
      <div class="error-state_content">
        <lib-icon name="circle-alert" size="xl" color="var(--color-error)" ariaLabel="Error" />
        <h3 class="error-state_title">{{ title() || 'Something went wrong' }}</h3>
        @if (message()) {
          <p class="error-state_message">{{ message() }}</p>
        }
        @if (showRetry()) {
          <lib-button
            variant="primary"
            [leftIcon]="'refresh-cw'"
            (clicked)="onRetry.emit()"
            class="error-state_button"
          >
            {{ retryLabel() }}
          </lib-button>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .error-state {
        @apply flex flex-col items-center justify-center;
        @apply w-full h-full;
        @apply py-12 px-4;
        min-height: 200px;
      }

      .error-state_content {
        @apply flex flex-col items-center justify-center;
        @apply gap-3;
        @apply text-center;
        @apply w-full;
        max-width: 400px;
      }

      .error-state_button {
        @apply mt-4;
      }

      .error-state_title {
        @apply text-lg font-semibold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .error-state_message {
        @apply text-sm;
        color: var(--color-text-secondary);
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ErrorState {
  title = input<string>('');
  message = input<string>('');
  retryLabel = input<string>('Try Again');
  showRetry = input<boolean>(true);

  onRetry = output<void>();
}
