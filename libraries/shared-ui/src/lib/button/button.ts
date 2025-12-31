import { Component, input, output, computed, booleanAttribute } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, IconName } from '../icon/icon';
import { Size, DEFAULT_SIZE } from '../types';

@Component({
  selector: 'lib-button',
  imports: [Icon, RouterLink],
  host: {
    '[class.button-host--full-width]': 'fullWidth()',
  },
  template: `
    <button
      class="button"
      [class.button--primary]="normalizedVariant() === 'primary'"
      [class.button--secondary]="normalizedVariant() === 'secondary'"
      [class.button--destructive]="normalizedVariant() === 'destructive'"
      [class.button--outline]="normalizedVariant() === 'outline'"
      [class.button--ghost]="normalizedVariant() === 'ghost'"
      [class.button--link]="normalizedVariant() === 'link'"
      [class.button--xs]="size() === 'xs'"
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
        @apply focus:outline-none;
        @apply rounded-md; /* Notion-style rounded corners */
        position: relative; /* For absolute positioned link */
        /* Default styles will be overridden by variant classes */
      }

      /* Full width button */
      :host.button-host--full-width {
        @apply flex w-full;
        display: block;
      }

      .button--full-width {
        @apply flex w-full;
      }

      .button--full-width .button_content {
        width: 100%;
      }

      .button:focus,
      .button:focus-visible {
        outline: none;
        box-shadow: none;
        ring: none;
      }

      /* Variants */
      .button--primary {
        @apply bg-primary text-primary-foreground border-primary;
        @apply font-semibold shadow-md;
      }

      .button--primary:not(.button--disabled):hover {
        @apply bg-primary/90 border-primary/90 shadow-lg;
      }

      .button--secondary {
        @apply bg-secondary text-secondary-foreground border-border;
        @apply font-medium;
      }

      .button--secondary:not(.button--disabled):hover {
        @apply bg-secondary/80;
      }

      .button--destructive {
        @apply bg-destructive text-destructive-foreground border-destructive;
        @apply font-medium;
      }

      .button--destructive:not(.button--disabled):hover {
        @apply bg-destructive/90 border-destructive/90;
      }

      .button--outline {
        @apply bg-transparent text-foreground border-border;
        @apply font-medium;
      }

      .button--outline:not(.button--disabled):hover {
        @apply bg-accent text-accent-foreground border-accent;
      }

      .button--ghost {
        @apply bg-transparent text-foreground border-transparent;
        @apply font-medium;
      }

      .button--ghost:not(.button--disabled):hover {
        @apply bg-accent text-accent-foreground;
      }

      .button--link {
        @apply bg-transparent text-primary border-transparent;
        @apply font-medium;
        @apply underline-offset-4;
        @apply shadow-none;
      }

      .button--link:not(.button--disabled):hover {
        @apply underline text-primary/80;
      }

      /* Sizes */
      .button--xs {
        @apply px-2 py-1 text-xs;
        min-height: 1.75rem;
      }

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

      .button--icon-only.button--xs {
        @apply w-6 h-6;
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
  variant = input<
    'primary' | 'link' | 'ghost' | 'secondary' | 'destructive' | 'outline' | undefined
  >('primary');
  size = input<Size>(DEFAULT_SIZE);
  disabled = input(false, { transform: booleanAttribute });
  loading = input(false, { transform: booleanAttribute });
  iconOnly = input(false, { transform: booleanAttribute });
  fullWidth = input(false, { transform: booleanAttribute });
  type = input<'button' | 'submit' | 'reset'>('button');
  leftIcon = input<IconName | undefined | null>(undefined);
  rightIcon = input<IconName | undefined | null>(undefined);
  link = input<string | string[] | undefined | null>(undefined); // RouterLink - if provided, renders <a> instead of <button>

  // Output
  clicked = output<MouseEvent>();

  // Computed
  readonly normalizedVariant = computed(() => {
    return this.variant() ?? 'primary';
  });

  readonly spinnerSize = computed(() => {
    const size = this.size();
    const sizeMap: Record<string, 'xs' | 'sm' | 'md'> = {
      xs: 'xs',
      sm: 'xs',
      md: 'sm',
      lg: 'md',
    };
    return sizeMap[size] || 'sm';
  });

  readonly iconSize = computed(() => {
    const size = this.size();
    const sizeMap: Record<string, 'xs' | 'sm' | 'md'> = {
      xs: 'xs',
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
