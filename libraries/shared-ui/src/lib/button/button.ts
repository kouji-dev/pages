import { Component, input, output, computed } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, IconName } from '../icon/icon';

@Component({
  selector: 'lib-button',
  imports: [Icon, RouterLink],
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
      [class.button--full-width]="fullWidth()"
      [disabled]="!link() && (disabled() || loading())"
      [type]="link() ? 'button' : type()"
      (click)="onClick($event)"
    >
      @if (link()) {
        <a
          class="button_link"
          [routerLink]="link()!"
          [attr.aria-disabled]="disabled() || loading() ? 'true' : null"
          [tabindex]="disabled() || loading() ? -1 : 0"
          (click)="onLinkClick($event)"
        >
        </a>
      }
      @if (loading()) {
        <lib-icon
          name="loader"
          [size]="spinnerSize()"
          animation="spin"
          [ariaHidden]="true"
          class="button_spinner"
        ></lib-icon>
      } @else {
        <span class="button_content">
          @if (leftIcon()) {
            <lib-icon
              [name]="leftIcon()!"
              [size]="iconSize()"
              class="button_icon button_icon--left"
            ></lib-icon>
          }
          <ng-content></ng-content>
          @if (rightIcon()) {
            <lib-icon
              [name]="rightIcon()!"
              [size]="iconSize()"
              class="button_icon button_icon--right"
            ></lib-icon>
          }
        </span>
      }
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
        position: relative; /* For absolute positioned link */
        /* Default styles will be overridden by variant classes */
      }

      /* Full width button */
      .button--full-width {
        @apply flex w-full;
      }

      .button--full-width .button_content {
        width: 100%;
      }

      .button:focus-visible {
        @apply outline-2;
        @apply outline-border-focus;
        outline-offset: 2px;
      }

      /* Variants */
      .button--primary {
        @apply text-text-inverse; /* White text */
        @apply bg-text-primary; /* Pure black background - Notion style */
        @apply border-text-primary;
      }

      .button--primary:not(.button--disabled):hover {
        @apply bg-gray-800; /* Dark gray on hover */
        @apply border-gray-800;
      }

      .button--secondary {
        @apply text-text-primary; /* Black text */
        @apply bg-bg-tertiary; /* Light gray/beige background - Notion style */
        @apply border-border-default;
      }

      .button--secondary:not(.button--disabled):hover {
        @apply bg-gray-300; /* Slightly darker on hover */
        @apply border-border-hover;
      }

      .button--danger {
        @apply text-text-inverse; /* White text */
        @apply bg-error; /* Red background */
        @apply border-error;
      }

      .button--danger:not(.button--disabled):hover {
        @apply bg-error-600; /* Darker red on hover */
        @apply border-error-600;
      }

      .button--ghost {
        @apply text-text-primary; /* Black text */
        background-color: transparent;
        border-color: transparent;
      }

      .button--ghost:not(.button--disabled):hover {
        @apply bg-bg-hover; /* Light hover background - Notion style */
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

      /* Icons */
      .button_icon {
        flex-shrink: 0;
      }

      .button_icon--left {
        @apply mr-1;
      }

      .button_icon--right {
        @apply ml-1;
      }

      .button--icon-only .button_icon {
        @apply m-0;
      }

      /* Spinner */
      .button_spinner {
        @apply absolute flex items-center justify-center;
      }

      /* Ensure spinner is visible when loading */
      .button:has(.button_spinner) {
        position: relative;
      }

      /* Link inside button */
      .button_link {
        @apply absolute inset-0;
        @apply z-10;
        text-decoration: none;
        @apply cursor-pointer;
      }

      .button--disabled .button_link {
        pointer-events: none;
      }
    `,
  ],
})
export class Button {
  // Inputs
  variant = input<'primary' | 'secondary' | 'danger' | 'ghost'>('primary');
  size = input<'sm' | 'md' | 'lg'>('md');
  disabled = input(false);
  loading = input(false);
  iconOnly = input(false);
  fullWidth = input(false);
  type = input<'button' | 'submit' | 'reset'>('button');
  leftIcon = input<IconName | null>(null);
  rightIcon = input<IconName | null>(null);
  link = input<string | string[] | null>(null); // RouterLink - if provided, renders <a> instead of <button>

  // Output
  clicked = output<MouseEvent>();

  // Computed
  readonly spinnerSize = computed(() => {
    const size = this.size();
    const sizeMap: Record<string, 'xs' | 'sm' | 'md'> = {
      sm: 'xs',
      md: 'sm',
      lg: 'md',
    };
    return sizeMap[size] || 'sm';
  });

  readonly iconSize = computed(() => {
    const size = this.size();
    const sizeMap: Record<string, 'xs' | 'sm' | 'md'> = {
      sm: 'xs',
      md: 'sm',
      lg: 'md',
    };
    return sizeMap[size] || 'sm';
  });

  // Methods
  onClick(event: MouseEvent): void {
    if (this.disabled() || this.loading()) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }
    // If link is provided, let the link handle navigation
    if (this.link()) {
      return;
    }
    // For submit buttons, don't prevent default - let the form handle submission
    if (this.type() === 'submit') {
      // Still emit the clicked event for handlers that want to listen to it
      this.clicked.emit(event);
      // Don't prevent default - allow form submission to proceed
      return;
    }
    this.clicked.emit(event);
  }

  onLinkClick(event: MouseEvent): void {
    if (this.disabled() || this.loading()) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }
    // Link handles navigation via RouterLink
    this.clicked.emit(event);
  }
}
