import { Component, input, computed, ChangeDetectionStrategy } from '@angular/core';
import { Icon, IconSize } from '../icon/icon';

export type LoadingStateSize = 'sm' | 'md' | 'lg';
export type LoadingStateColor = 'default' | 'primary' | 'secondary';

@Component({
  selector: 'lib-loading-state',
  imports: [Icon],
  template: `
    <div class="loading-state">
      <div class="loading-state_content">
        <lib-icon
          name="loader"
          [size]="iconSize()"
          [color]="iconColor()"
          animation="spin"
          [ariaLabel]="ariaLabel() || 'Loading'"
        />
        @if (message()) {
          <p class="loading-state_message">{{ message() }}</p>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .loading-state {
        @apply flex flex-col items-center justify-center;
        @apply w-full h-full;
        @apply py-12 px-4;
        min-height: 200px;
      }

      .loading-state_content {
        @apply flex flex-col items-center justify-center;
        @apply gap-3;
        @apply w-full;
      }

      .loading-state_message {
        @apply text-sm font-medium;
        color: var(--color-text-secondary);
        margin: 0;
        text-align: center;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoadingState {
  message = input<string>('');
  size = input<LoadingStateSize>('md');
  color = input<LoadingStateColor>('default');
  ariaLabel = input<string>('');

  readonly iconSize = computed<IconSize>(() => {
    const size = this.size();
    const sizeMap: Record<LoadingStateSize, IconSize> = {
      sm: 'sm',
      md: 'md',
      lg: 'lg',
    };
    return sizeMap[size] || 'md';
  });

  readonly iconColor = computed<string | undefined>(() => {
    const color = this.color();
    const colorMap: Record<LoadingStateColor, string> = {
      default: 'var(--color-text-primary)',
      primary: 'var(--color-primary-500)',
      secondary: 'var(--color-secondary-500)',
    };
    return colorMap[color] || colorMap.default;
  });
}
