import { Component, input, computed, ChangeDetectionStrategy } from '@angular/core';

export type SpinnerSize = 'sm' | 'md' | 'lg';
export type SpinnerColor = 'default' | 'primary' | 'secondary' | 'white';

@Component({
  selector: 'lib-spinner',
  template: `
    <div
      class="spinner"
      [class.spinner--sm]="size() === 'sm'"
      [class.spinner--md]="size() === 'md'"
      [class.spinner--lg]="size() === 'lg'"
      [class.spinner--default]="color() === 'default'"
      [class.spinner--primary]="color() === 'primary'"
      [class.spinner--secondary]="color() === 'secondary'"
      [class.spinner--white]="color() === 'white'"
      [attr.aria-label]="ariaLabel() || 'Loading'"
      [attr.aria-hidden]="ariaHidden() ? 'true' : null"
      role="status"
    >
      <svg
        class="spinner_circle"
        viewBox="0 0 24 24"
        [attr.width]="computedSize()"
        [attr.height]="computedSize()"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          class="spinner_circle-path"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-dasharray="32"
          stroke-dashoffset="32"
        />
      </svg>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .spinner {
        @apply inline-flex items-center justify-center;
        @apply animate-spin;
        flex-shrink: 0;
        color: var(--color-text-primary);
      }

      .spinner_circle {
        display: block;
      }

      .spinner_circle-path {
        animation: spinner-dash 1.5s ease-in-out infinite;
        transform-origin: center;
      }

      /* Size variants - using spacing scale */
      .spinner--sm {
        @apply w-4 h-4; /* 16px - spacing-4 */
      }

      .spinner--sm .spinner_circle {
        @apply w-4 h-4;
      }

      .spinner--md {
        @apply w-5 h-5; /* 20px - 1.25rem */
      }

      .spinner--md .spinner_circle {
        @apply w-5 h-5;
      }

      .spinner--lg {
        @apply w-6 h-6; /* 24px - spacing-6 */
      }

      .spinner--lg .spinner_circle {
        @apply w-6 h-6;
      }

      /* Color variants */
      .spinner--default {
        color: var(--color-text-primary);
      }

      .spinner--primary {
        color: var(--color-primary-500);
      }

      .spinner--secondary {
        color: var(--color-secondary-500);
      }

      .spinner--white {
        color: var(--color-text-inverse);
      }

      /* Spinner animation */
      @keyframes spinner-dash {
        0% {
          stroke-dasharray: 1, 150;
          stroke-dashoffset: 0;
        }
        50% {
          stroke-dasharray: 90, 150;
          stroke-dashoffset: -35;
        }
        100% {
          stroke-dasharray: 90, 150;
          stroke-dashoffset: -124;
        }
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Spinner {
  // Inputs
  size = input<SpinnerSize>('md');
  color = input<SpinnerColor>('default');
  ariaLabel = input<string>('');
  ariaHidden = input<boolean>(false);

  // Computed
  readonly computedSize = computed(() => {
    const size = this.size();
    const sizeMap: Record<SpinnerSize, number> = {
      sm: 16,
      md: 20,
      lg: 24,
    };
    return sizeMap[size] || 20;
  });
}
