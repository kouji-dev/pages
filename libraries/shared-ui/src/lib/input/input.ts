import {
  Component,
  input,
  output,
  model,
  computed,
  signal,
  booleanAttribute,
  ChangeDetectionStrategy,
} from '@angular/core';
import { Icon, IconName } from '../icon/icon';

export type InputType =
  | 'text'
  | 'email'
  | 'password'
  | 'number'
  | 'tel'
  | 'url'
  | 'search'
  | 'date'
  | 'time'
  | 'datetime-local'
  | 'textarea';

@Component({
  selector: 'lib-input',
  imports: [Icon],
  template: `
    <div class="input-wrapper" [class.input-wrapper--error]="errorMessage()">
      @if (label()) {
        <label [for]="inputId()" class="input-label">
          {{ label() }}
          @if (required()) {
            <span class="input-label-required" aria-label="required">*</span>
          }
        </label>
      }

      <div class="input-container" [class.input-container--disabled]="disabled()">
        @if (leftIcon() && leftIcon()!.trim() && type() !== 'textarea') {
          <span class="input-icon input-icon--left">
            <lib-icon [name]="leftIcon()!" size="sm" [ariaHidden]="true"></lib-icon>
          </span>
        }

        @if (type() === 'textarea') {
          <textarea
            [id]="inputId()"
            class="input input--textarea"
            [class.input--error]="errorMessage()"
            [class.input--disabled]="disabled()"
            [class.input--readonly]="readonly()"
            [placeholder]="placeholder()"
            [disabled]="disabled()"
            [readonly]="readonly()"
            [required]="required()"
            [rows]="rows()"
            [attr.aria-invalid]="errorMessage() ? 'true' : null"
            [attr.aria-describedby]="ariaDescribedBy()"
            (input)="onInput($event)"
            (focus)="onFocus($event)"
            (blur)="onBlur($event)"
            >{{ model() }}</textarea
          >
        } @else {
          <input
            [id]="inputId()"
            class="input"
            [class.input--error]="errorMessage()"
            [class.input--disabled]="disabled()"
            [class.input--readonly]="readonly()"
            [class.input--with-left-icon]="leftIcon() && leftIcon()!.trim()"
            [class.input--with-right-icon]="
              (rightIcon() && rightIcon()!.trim()) || showPasswordToggle() || type() === 'number'
            "
            [type]="computedInputType()"
            [placeholder]="placeholder()"
            [value]="model()"
            [disabled]="disabled()"
            [readonly]="readonly()"
            [required]="required()"
            [attr.aria-invalid]="errorMessage() ? 'true' : null"
            [attr.aria-describedby]="ariaDescribedBy()"
            (input)="onInput($event)"
            (focus)="onFocus($event)"
            (blur)="onBlur($event)"
          />
        }

        @if (type() === 'number' && !disabled() && !readonly()) {
          <div class="input-number-spinner">
            <button
              type="button"
              class="input-number-spinner-button input-number-spinner-button--up"
              [attr.aria-label]="'Increment'"
              (click)="incrementNumber($event)"
              tabindex="-1"
            >
              <lib-icon name="chevron-up" size="xs" [ariaHidden]="true"></lib-icon>
            </button>
            <button
              type="button"
              class="input-number-spinner-button input-number-spinner-button--down"
              [attr.aria-label]="'Decrement'"
              (click)="decrementNumber($event)"
              tabindex="-1"
            >
              <lib-icon name="chevron-down" size="xs" [ariaHidden]="true"></lib-icon>
            </button>
          </div>
        }

        @if (showPasswordToggle() && type() === 'password') {
          <button
            type="button"
            class="input-icon input-icon--right input-password-toggle"
            [attr.aria-label]="showPassword() ? 'Hide password' : 'Show password'"
            (click)="togglePasswordVisibility()"
            tabindex="-1"
          >
            <lib-icon
              [name]="showPassword() ? 'eye-off' : 'eye'"
              size="sm"
              [ariaHidden]="true"
            ></lib-icon>
          </button>
        } @else if (rightIcon() && rightIcon()!.trim()) {
          <span class="input-icon input-icon--right">
            <lib-icon [name]="rightIcon()!" size="sm" [ariaHidden]="true"></lib-icon>
          </span>
        }
      </div>

      @if (helperText() && !errorMessage()) {
        <span [id]="helperTextId()" class="input-helper-text">
          {{ helperText() }}
        </span>
      }

      @if (errorMessage()) {
        <span [id]="errorMessageId()" class="input-error-message" role="alert">
          <lib-icon
            name="circle-alert"
            size="xs"
            [ariaHidden]="true"
            class="input-error-icon"
          ></lib-icon>
          {{ errorMessage() }}
        </span>
      }
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .input-wrapper {
        @apply flex flex-col gap-1.5;
        width: 100%;
      }

      .input-label {
        @apply text-sm font-medium;
        @apply text-text-primary;
        @apply leading-normal;
      }

      .input-label-required {
        @apply ml-0.5;
        @apply text-error;
      }

      .input-container {
        @apply relative flex items-center;
        position: relative;
      }

      .input-container--disabled {
        @apply opacity-60 cursor-not-allowed;
      }

      .input {
        @apply w-full;
        @apply px-3 py-2;
        @apply text-base;
        @apply border rounded-md;
        @apply bg-bg-primary;
        @apply transition-colors;
        @apply focus:outline-none;
        @apply text-text-primary;
        @apply border-border-default;
        @apply font-sans;
        min-height: 2.5rem;
        color: var(--color-text-primary);
      }

      .input--textarea {
        @apply resize-y;
        min-height: 6rem; /* Default for textarea */
        @apply leading-normal;
      }

      .input::placeholder {
        @apply text-text-tertiary;
        opacity: 1;
      }

      .input:hover:not(:disabled):not(:read-only):not(.input--error) {
        @apply border-border-hover;
      }

      .input:focus:not(:disabled):not(:read-only) {
        @apply border-border-focus;
        @apply outline-2;
        @apply outline-border-focus;
        outline-offset: -2px;
      }

      .input--error {
        @apply border-border-error;
      }

      .input--error:focus {
        @apply border-border-error;
        @apply outline-border-error;
      }

      .input--disabled {
        @apply cursor-not-allowed;
        @apply bg-bg-tertiary;
        @apply border-border-default;
      }

      .input--readonly {
        @apply cursor-default;
        @apply bg-bg-tertiary;
        @apply border-border-default;
      }

      /* Number input spinner styling - hide native spinners */
      .input[type='number'] {
        -moz-appearance: textfield; /* Firefox - hides spinners */
      }

      /* Chrome, Safari, Edge, Opera - Hide native spinners */
      .input[type='number']::-webkit-outer-spin-button,
      .input[type='number']::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
      }

      /* Custom number spinner buttons */
      .input-number-spinner {
        @apply absolute right-0 flex flex-col;
        @apply border-l border-solid;
        @apply border-l-border-default;
        height: 100%;
        justify-content: center;
        gap: 0;
        top: 0;
        margin: 0;
        padding: 0;
      }

      .input-number-spinner-button {
        @apply flex items-center justify-center;
        @apply border-none bg-transparent;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply p-0.5;
        @apply focus:outline-none;
        width: 1.5rem;
        height: 50%;
        min-height: 0.875rem;
        @apply text-text-tertiary;
        border-radius: 0;
        margin: 0;
      }

      .input-number-spinner-button:hover {
        @apply bg-bg-hover;
        @apply text-text-primary;
      }

      .input-number-spinner-button:active {
        @apply bg-bg-active;
      }

      .input-number-spinner-button--up {
        @apply border-b;
        @apply border-border-default;
        border-top-right-radius: 0.375rem;
        border-bottom-right-radius: 0;
      }

      .input-number-spinner-button--down {
        border-bottom-right-radius: 0.375rem;
        border-top-right-radius: 0;
      }

      .input--with-left-icon {
        @apply pl-9;
      }

      .input--with-right-icon {
        @apply pr-9;
      }

      .input-icon {
        @apply absolute flex items-center justify-center;
        @apply pointer-events-none;
        @apply text-text-tertiary;
        z-index: 1;
      }

      .input-icon--left {
        @apply left-3;
      }

      .input-icon--right {
        @apply right-3;
      }

      .input-password-toggle {
        @apply pointer-events-auto cursor-pointer;
        @apply border-none bg-transparent p-0;
        @apply hover:opacity-70;
        @apply focus:outline-none focus:ring-2 focus:ring-offset-1;
        @apply text-text-secondary;
        border-radius: 0.25rem;
      }

      .input-password-toggle:focus-visible {
        @apply outline-2;
        @apply outline-border-focus;
        outline-offset: 2px;
      }

      .input-helper-text {
        @apply text-xs;
        @apply text-text-tertiary;
        @apply leading-normal;
      }

      .input-error-message {
        @apply flex items-center gap-1.5;
        @apply text-xs font-medium;
        @apply text-error;
        @apply leading-normal;
      }

      .input-error-icon {
        flex-shrink: 0;
      }

      .input-wrapper--error .input-label {
        @apply text-error;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Input {
  // Model for two-way binding
  model = model<string>('');

  // Inputs
  type = input<InputType>('text');
  placeholder = input<string>('');
  label = input<string>('');
  helperText = input<string>('');
  errorMessage = input<string>('');
  required = input(false, { transform: booleanAttribute });
  disabled = input(false, { transform: booleanAttribute });
  readonly = input(false, { transform: booleanAttribute });
  leftIcon = input<IconName | null>(null);
  rightIcon = input<IconName | null>(null);
  showPasswordToggle = input(false, { transform: booleanAttribute });
  rows = input<number>(4); // For textarea

  // Outputs
  focused = output<FocusEvent>();
  blurred = output<FocusEvent>();

  // Internal state
  readonly showPassword = signal(false);
  private uniqueId = `input-${Math.random().toString(36).substring(2, 9)}`;

  // Computed
  readonly inputId = computed(() => this.uniqueId);
  readonly helperTextId = computed(() => `${this.uniqueId}-helper`);
  readonly errorMessageId = computed(() => `${this.uniqueId}-error`);

  readonly ariaDescribedBy = computed(() => {
    const ids: string[] = [];
    if (this.helperText() && !this.errorMessage()) {
      ids.push(this.helperTextId());
    }
    if (this.errorMessage()) {
      ids.push(this.errorMessageId());
    }
    return ids.length > 0 ? ids.join(' ') : undefined;
  });

  readonly computedInputType = computed(() => {
    if (this.type() === 'password' && this.showPasswordToggle() && this.showPassword()) {
      return 'text';
    }
    return this.type();
  });

  // Internal state
  private inputElement = signal<HTMLInputElement | HTMLTextAreaElement | null>(null);

  // Methods
  onInput(event: Event): void {
    const target = event.target as HTMLInputElement | HTMLTextAreaElement;
    this.inputElement.set(target);
    this.model.set(target.value);
  }

  onFocus(event: FocusEvent): void {
    this.focused.emit(event);
  }

  onBlur(event: FocusEvent): void {
    this.blurred.emit(event);
  }

  togglePasswordVisibility(): void {
    this.showPassword.update((show) => !show);
  }

  incrementNumber(event: Event): void {
    event.preventDefault();
    const currentValue = parseFloat(this.model()) || 0;
    const step = 1; // Could be made configurable
    this.model.set(String(currentValue + step));
    this.inputElement()?.focus();
  }

  decrementNumber(event: Event): void {
    event.preventDefault();
    const currentValue = parseFloat(this.model()) || 0;
    const step = 1; // Could be made configurable
    this.model.set(String(currentValue - step));
    this.inputElement()?.focus();
  }
}
