import { Component, input, computed, ChangeDetectionStrategy } from '@angular/core';
import { Icon, IconSize, IconColor } from '../icon/icon';

export type SpinnerSize = 'sm' | 'md' | 'lg';
export type SpinnerColor = 'default' | 'primary' | 'secondary' | 'white';

@Component({
  selector: 'lib-spinner-content',
  imports: [Icon],
  template: `
    <div class="spinner-content">
      <div class="spinner-content_backdrop"></div>
      <div class="spinner-content_loader">
        <lib-icon
          name="loader"
          [size]="iconSize()"
          [color]="iconColor()"
          animation="spin"
          [ariaLabel]="ariaLabel() || 'Loading'"
        />
        @if (message()) {
          <p class="spinner-content_message">{{ message() }}</p>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .spinner-content {
        @apply absolute inset-0;
        @apply flex items-center justify-center;
        @apply pointer-events-none;
        z-index: 10;
      }

      .spinner-content_backdrop {
        @apply absolute inset-0;
        @apply bg-background/80;
        backdrop-filter: blur(2px);
      }

      .spinner-content_loader {
        @apply relative z-10;
        @apply flex flex-col items-center justify-center;
        @apply gap-3;
      }

      .spinner-content_message {
        @apply text-sm font-medium;
        @apply text-foreground;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SpinnerContent {
  size = input<SpinnerSize>('md');
  color = input<SpinnerColor>('default');
  message = input<string>('');
  ariaLabel = input<string>('');

  // Computed: map spinner size to icon size
  readonly iconSize = computed<IconSize>(() => {
    const size = this.size();
    const sizeMap: Record<SpinnerSize, IconSize> = {
      sm: 'sm',
      md: 'md',
      lg: 'lg',
    };
    return sizeMap[size] || 'md';
  });

  // Computed: map spinner color to icon color name
  readonly iconColor = computed<IconColor | undefined>(() => {
    const color = this.color();
    const colorMap: Record<SpinnerColor, IconColor> = {
      default: 'foreground',
      primary: 'primary-500',
      secondary: 'secondary-500',
      white: 'primary-foreground',
    };
    return colorMap[color] || colorMap.default;
  });
}
