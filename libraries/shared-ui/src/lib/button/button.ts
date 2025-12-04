import { Component, input, output, computed } from '@angular/core';

@Component({
  selector: 'lib-button',
  imports: [],
  template: `
    <button
      class="button"
      [class.button--primary]="variant() === 'primary'"
      [class.button--secondary]="variant() === 'secondary'"
      [class.button--danger]="variant() === 'danger'"
      [class.button--ghost]="variant() === 'ghost'"
      [class.button--sm]="size() === 'sm'"
      [class.button--md]="size() === 'md'"
      [class.button--lg]="size() === 'lg'"
      [class.button--disabled]="disabled() || loading()"
      [class.button--icon-only]="iconOnly()"
      [disabled]="disabled() || loading()"
      [type]="type()"
      (click)="onClick($event)"
    >
      @if (loading()) {
        <span class="button_spinner" aria-hidden="true">
          <svg
            class="button_spinner-icon"
            fill="none"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              class="button_spinner-circle"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
              stroke-linecap="round"
              stroke-dasharray="32"
              stroke-dashoffset="32"
            >
              <animate
                attributeName="stroke-dasharray"
                dur="2s"
                values="0 32;16 16;0 32;0 32"
                repeatCount="indefinite"
              />
              <animate
                attributeName="stroke-dashoffset"
                dur="2s"
                values="0;-16;-32;-32"
                repeatCount="indefinite"
              />
            </circle>
          </svg>
        </span>
      }
      <span class="button_content" [class.button_content--hidden]="loading()">
        <ng-content></ng-content>
      </span>
    </button>
  `,
  styles: [
    `
      @reference "#theme";

      .button {
        @apply inline-flex items-center justify-center gap-2;
        @apply font-medium transition-colors;
        @apply border;
        @apply cursor-pointer;
        @apply focus:outline-none focus:ring-2 focus:ring-offset-2;
        @apply rounded-md; /* Notion-style rounded corners */
        /* Default styles will be overridden by variant classes */
      }

      .button:focus-visible {
        outline: 2px solid var(--color-border-focus);
        outline-offset: 2px;
      }

      /* Variants */
      .button--primary {
        color: var(--color-text-inverse); /* White text */
        background-color: var(--color-text-primary); /* Pure black background - Notion style */
        border-color: var(--color-text-primary);
      }

      .button--primary:not(.button--disabled):hover {
        background-color: var(--color-gray-800); /* Dark gray on hover */
        border-color: var(--color-gray-800);
      }

      .button--secondary {
        color: var(--color-text-primary); /* Black text */
        background-color: var(--color-bg-tertiary); /* Light gray/beige background - Notion style */
        border-color: var(--color-border-default);
      }

      .button--secondary:not(.button--disabled):hover {
        background-color: var(--color-gray-300); /* Slightly darker on hover */
        border-color: var(--color-border-hover);
      }

      .button--danger {
        color: var(--color-text-inverse); /* White text */
        background-color: var(--color-error); /* Red background */
        border-color: var(--color-error);
      }

      .button--danger:not(.button--disabled):hover {
        background-color: var(--color-error-600); /* Darker red on hover */
        border-color: var(--color-error-600);
      }

      .button--ghost {
        color: var(--color-text-primary); /* Black text */
        background-color: transparent;
        border-color: transparent;
      }

      .button--ghost:not(.button--disabled):hover {
        background-color: var(--color-bg-hover); /* Light hover background - Notion style */
        border-color: transparent;
      }

      /* Sizes */
      .button--sm {
        @apply px-3 py-1.5 text-sm;
        min-height: 2rem;
      }

      .button--md {
        @apply px-4 py-2 text-base;
        min-height: 2.5rem;
      }

      .button--lg {
        @apply px-6 py-3 text-lg;
        min-height: 3rem;
      }

      /* Disabled State */
      .button--disabled {
        @apply opacity-50 cursor-not-allowed;
        pointer-events: none;
      }

      /* Icon Only */
      .button--icon-only {
        @apply p-0;
        aspect-ratio: 1;
      }

      .button--icon-only.button--sm {
        @apply w-8 h-8;
      }

      .button--icon-only.button--md {
        @apply w-10 h-10;
      }

      .button--icon-only.button--lg {
        @apply w-12 h-12;
      }

      /* Content */
      .button_content {
        @apply flex items-center gap-2;
      }

      .button_content--hidden {
        @apply opacity-0;
      }

      /* Spinner */
      .button_spinner {
        @apply absolute flex items-center justify-center;
      }

      .button_spinner-icon {
        @apply animate-spin;
        width: 1em;
        height: 1em;
        color: currentColor;
      }

      .button_spinner-circle {
        opacity: 0.25;
      }

      /* Ensure spinner is visible when loading */
      .button:has(.button_spinner) {
        position: relative;
      }
    `,
  ],
  standalone: true,
})
export class Button {
  // Inputs
  variant = input<'primary' | 'secondary' | 'danger' | 'ghost'>('primary');
  size = input<'sm' | 'md' | 'lg'>('md');
  disabled = input(false);
  loading = input(false);
  iconOnly = input(false);
  type = input<'button' | 'submit' | 'reset'>('button');

  // Output
  clicked = output<MouseEvent>();

  // Methods
  onClick(event: MouseEvent): void {
    if (this.disabled() || this.loading()) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }
    this.clicked.emit(event);
  }
}
