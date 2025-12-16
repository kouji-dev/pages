import {
  Component,
  input,
  model,
  computed,
  signal,
  ChangeDetectionStrategy,
  inject,
  ElementRef,
  ViewChild,
  TemplateRef,
  ViewContainerRef,
  DestroyRef,
  effect,
  HostListener,
  booleanAttribute,
  forwardRef,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { Overlay, OverlayRef, OverlayConfig, ConnectedPosition } from '@angular/cdk/overlay';
import { TemplatePortal } from '@angular/cdk/portal';
import { Icon, IconName } from '../icon/icon';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface SelectOption<T = any> {
  value: T;
  label: string;
  icon?: IconName;
  iconColor?: string;
  disabled?: boolean;
  [key: string]: any; // Allow additional properties for custom templates
}

@Component({
  selector: 'lib-select',
  imports: [Icon, CommonModule, FormsModule],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => Select),
      multi: true,
    },
  ],
  template: `
    <div class="select-wrapper" [class.select-wrapper--error]="errorMessage()">
      @if (label()) {
        <label [for]="selectId()" class="select-label">
          {{ label() }}
          @if (required()) {
            <span class="select-label-required" aria-label="required">*</span>
          }
        </label>
      }

      <div class="select-container" [class.select-container--disabled]="isDisabled()">
        <button
          type="button"
          [id]="selectId()"
          class="select-trigger"
          [class.select-trigger--error]="errorMessage()"
          [class.select-trigger--disabled]="isDisabled()"
          [class.select-trigger--open]="isOpen()"
          [disabled]="isDisabled()"
          (click)="toggle()"
          (blur)="onTouched()"
          [attr.aria-haspopup]="'listbox'"
          [attr.aria-expanded]="isOpen()"
          [attr.aria-invalid]="errorMessage() ? 'true' : null"
          [attr.aria-describedby]="ariaDescribedBy()"
        >
          <span class="select-trigger-content">
            @if (selectedOption(); as option) {
              @if (optionTemplate()) {
                <ng-container
                  *ngTemplateOutlet="
                    optionTemplate()!;
                    context: { $implicit: option, selected: true }
                  "
                />
              } @else {
                @if (option.icon) {
                  <lib-icon [name]="option.icon" [size]="'xs'" [ngClass]="option.iconColor || ''" />
                }
                <span>{{ option.label }}</span>
              }
            } @else {
              <span class="select-placeholder">{{ placeholder() }}</span>
            }
          </span>
          <lib-icon
            name="chevron-down"
            [size]="'xs'"
            class="select-chevron"
            [class.select-chevron--open]="isOpen()"
          />
        </button>

        @if (helperText() && !errorMessage()) {
          <span [id]="helperTextId()" class="select-helper-text">{{ helperText() }}</span>
        }
        @if (errorMessage()) {
          <span [id]="errorId()" class="select-error-text">{{ errorMessage() }}</span>
        }
      </div>

      <!-- Dropdown Panel -->
      <ng-template #dropdownTemplate>
        <div class="select-dropdown" role="listbox">
          @if (searchable()) {
            <div class="select-search">
              <input
                type="text"
                class="select-search-input"
                placeholder="Search..."
                [(ngModel)]="searchQuery"
                (ngModelChange)="onSearchChange()"
                (click)="$event.stopPropagation()"
                #searchInput
              />
            </div>
          }

          <div class="select-options" role="listbox">
            @if (filteredOptions().length === 0) {
              <div class="select-empty">
                <span>{{ emptyText() }}</span>
              </div>
            } @else {
              @for (option of filteredOptions(); track getOptionValue(option)) {
                <button
                  type="button"
                  class="select-option"
                  [class.select-option--selected]="isSelected(option)"
                  [class.select-option--disabled]="option.disabled"
                  [disabled]="option.disabled"
                  role="option"
                  [attr.aria-selected]="isSelected(option)"
                  (click)="selectOption(option)"
                >
                  @if (optionTemplate()) {
                    <ng-container
                      *ngTemplateOutlet="
                        optionTemplate()!;
                        context: { $implicit: option, selected: isSelected(option) }
                      "
                    />
                  } @else {
                    @if (option.icon) {
                      <lib-icon
                        [name]="option.icon"
                        [size]="'xs'"
                        [ngClass]="option.iconColor || ''"
                      />
                    }
                    <span>{{ option.label }}</span>
                    @if (isSelected(option)) {
                      <lib-icon name="check" [size]="'xs'" class="select-option-check" />
                    }
                  }
                </button>
              }
            }
          </div>
        </div>
      </ng-template>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .select-wrapper {
        @apply flex flex-col;
        @apply gap-2;
      }

      .select-wrapper--error {
        @apply mb-4;
      }

      .select-label {
        @apply text-sm font-medium;
        @apply text-foreground;
      }

      .select-label-required {
        @apply text-error;
        @apply ml-1;
      }

      .select-container {
        @apply flex flex-col;
        @apply gap-1;
      }

      .select-container--disabled {
        @apply opacity-60;
        @apply cursor-not-allowed;
      }

      .select-trigger {
        @apply w-full;
        @apply px-3 py-2;
        @apply flex items-center justify-between;
        @apply gap-2;
        @apply border border-border;
        @apply rounded-md;
        @apply bg-background;
        @apply text-foreground;
        @apply text-left;
        @apply text-sm;
        @apply focus:outline-none focus:ring-2 focus:ring-primary;
        @apply transition-colors;
        @apply cursor-pointer;
      }

      .select-trigger:hover:not(:disabled) {
        @apply border-primary;
      }

      .select-trigger--error {
        @apply border-error;
        @apply focus:ring-error;
      }

      .select-trigger--disabled {
        @apply cursor-not-allowed;
        @apply opacity-60;
      }

      .select-trigger--open {
        @apply border-primary;
        @apply ring-2 ring-primary;
      }

      .select-trigger-content {
        @apply flex items-center gap-1.5;
        @apply flex-1;
        @apply min-w-0;
      }

      .select-placeholder {
        @apply text-muted-foreground;
      }

      .select-chevron {
        @apply flex-shrink-0;
        @apply text-muted-foreground;
        @apply transition-transform;
      }

      .select-chevron--open {
        @apply transform rotate-180;
      }

      .select-helper-text {
        @apply text-xs;
        @apply text-muted-foreground;
      }

      .select-error-text {
        @apply text-xs;
        @apply text-destructive;
      }

      .select-dropdown {
        @apply bg-card;
        @apply border border-border;
        @apply rounded-md;
        @apply shadow-lg;
        @apply w-full;
        @apply max-h-[300px];
        @apply overflow-hidden;
        @apply z-50;
      }

      .select-search {
        @apply p-2;
        @apply border-b border-border;
      }

      .select-search-input {
        @apply w-full;
        @apply px-2 py-1.5;
        @apply text-sm;
        @apply border border-border;
        @apply rounded;
        @apply bg-background;
        @apply text-foreground;
        @apply focus:outline-none focus:ring-2 focus:ring-ring;
      }

      .select-options {
        @apply py-1;
        @apply max-h-[250px];
        @apply overflow-y-auto;
      }

      .select-empty {
        @apply px-3 py-2;
        @apply text-sm;
        @apply text-muted-foreground;
        @apply text-center;
      }

      .select-option {
        @apply w-full;
        @apply px-3 py-2;
        @apply flex items-center gap-1.5;
        @apply text-left;
        @apply text-sm;
        @apply text-foreground;
        @apply bg-transparent;
        @apply border-none;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-muted;
      }

      .select-option--selected {
        @apply bg-primary/10;
        @apply text-primary;
        @apply font-medium;
      }

      .select-option--disabled {
        @apply opacity-50;
        @apply cursor-not-allowed;
        @apply hover:bg-transparent;
      }

      .select-option-check {
        @apply ml-auto;
        @apply flex-shrink-0;
        @apply text-primary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Select<T = any> implements ControlValueAccessor {
  private readonly overlay = inject(Overlay);
  private readonly elementRef = inject(ElementRef);
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly destroyRef = inject(DestroyRef);

  // Core inputs
  readonly options = input.required<SelectOption<T>[]>();
  readonly model = model<T | null>(null);
  readonly label = input<string>('');
  readonly placeholder = input<string>('Select an option...');
  readonly required = input(false, { transform: booleanAttribute });
  readonly disabled = input(false, { transform: booleanAttribute });
  readonly searchable = input(false, { transform: booleanAttribute });
  readonly emptyText = input<string>('No options found');
  readonly errorMessage = input<string>('');
  readonly helperText = input<string>('');

  // Custom template for option rendering
  readonly optionTemplate = input<TemplateRef<any>>();

  // Internal state
  readonly isOpen = signal(false);
  readonly searchQuery = signal('');

  // ControlValueAccessor implementation
  private onChange = (value: T | null) => {};
  onTouched = () => {};

  // Disabled state - can be controlled by input or form control
  private readonly formDisabledState = signal<boolean | undefined>(undefined);
  readonly isDisabled = computed(() => {
    const formDisabled = this.formDisabledState();
    if (formDisabled !== undefined) {
      return formDisabled;
    }
    return this.disabled();
  });

  @ViewChild('dropdownTemplate') dropdownTemplate!: TemplateRef<any>;
  @ViewChild('searchInput') searchInput?: ElementRef<HTMLInputElement>;

  private overlayRef: OverlayRef | null = null;
  private readonly _selectId = `select-${Math.random().toString(36).substr(2, 9)}`;

  // Computed
  readonly selectedOption = computed(() => {
    const value = this.model();
    if (value === null || value === undefined) return null;
    return this.options().find((opt) => this.getOptionValue(opt) === value) || null;
  });

  readonly filteredOptions = computed(() => {
    const query = this.searchQuery().toLowerCase().trim();
    if (!query) return this.options();

    return this.options().filter((option) => {
      return option.label.toLowerCase().includes(query);
    });
  });

  readonly selectId = computed(() => this._selectId);
  readonly helperTextId = computed(() => `${this._selectId}-helper`);
  readonly errorId = computed(() => `${this._selectId}-error`);
  readonly ariaDescribedBy = computed(() => {
    const ids: string[] = [];
    if (this.helperText() && !this.errorMessage()) {
      ids.push(this.helperTextId());
    }
    if (this.errorMessage()) {
      ids.push(this.errorId());
    }
    return ids.length > 0 ? ids.join(' ') : null;
  });

  // Effect to sync overlay with isOpen state
  private readonly syncOverlay = effect(() => {
    if (this.isOpen()) {
      this.openOverlay();
    } else {
      this.closeOverlay();
    }
  });

  // Effect to sync model changes with ControlValueAccessor
  private readonly syncModelToForm = effect(() => {
    const value = this.model();
    this.onChange(value);
  });

  constructor() {
    this.destroyRef.onDestroy(() => {
      this.closeOverlay();
    });
  }

  // ControlValueAccessor implementation
  writeValue(value: T | null): void {
    // Only update if value is different to avoid infinite loops
    const currentValue = this.model();
    if (currentValue !== value) {
      this.model.set(value);
    }
  }

  registerOnChange(fn: (value: T | null) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.formDisabledState.set(isDisabled);
  }

  toggle(): void {
    if (this.isDisabled()) return;
    this.isOpen.update((value) => !value);
  }

  selectOption(option: SelectOption<T>): void {
    if (option.disabled) return;
    this.model.set(this.getOptionValue(option));
    this.isOpen.set(false);
    this.searchQuery.set('');
    this.onTouched();
  }

  isSelected(option: SelectOption<T>): boolean {
    const value = this.model();
    if (value === null || value === undefined) return false;
    return this.getOptionValue(option) === value;
  }

  getOptionValue(option: SelectOption<T>): T {
    return option.value;
  }

  onSearchChange(): void {
    // Search is handled by filteredOptions computed
  }

  private openOverlay(): void {
    if (this.overlayRef) return;

    const config: OverlayConfig = {
      positionStrategy: this.getPositionStrategy(),
      scrollStrategy: this.overlay.scrollStrategies.close(),
      panelClass: ['lib-select-panel'],
      backdropClass: 'cdk-overlay-transparent-backdrop',
      hasBackdrop: true,
      disposeOnNavigation: true,
    };

    this.overlayRef = this.overlay.create(config);

    const portal = new TemplatePortal(this.dropdownTemplate, this.viewContainerRef);
    this.overlayRef.attach(portal);

    // Set the overlay width to match the trigger width
    const element = this.elementRef.nativeElement as HTMLElement;
    const triggerWidth = element.offsetWidth;
    if (this.overlayRef.overlayElement) {
      this.overlayRef.overlayElement.style.width = `${triggerWidth}px`;
    }

    // Focus search input if searchable
    if (this.searchable() && this.searchInput) {
      setTimeout(() => {
        this.searchInput?.nativeElement.focus();
      }, 0);
    }

    // Handle backdrop clicks
    this.overlayRef.backdropClick().subscribe(() => {
      this.isOpen.set(false);
    });

    // Handle escape key
    this.overlayRef.keydownEvents().subscribe((event) => {
      if (event.key === 'Escape') {
        this.isOpen.set(false);
      }
    });
  }

  private closeOverlay(): void {
    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
    }
    this.searchQuery.set('');
  }

  private getPositionStrategy() {
    const positions: ConnectedPosition[] = [
      { originX: 'start', originY: 'bottom', overlayX: 'start', overlayY: 'top' },
      { originX: 'start', originY: 'top', overlayX: 'start', overlayY: 'bottom' },
    ];

    return this.overlay
      .position()
      .flexibleConnectedTo(this.elementRef)
      .withPositions(positions)
      .withDefaultOffsetY(4)
      .withFlexibleDimensions(false)
      .withPush(false);
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    if (!this.isOpen()) return;

    const target = event.target as Element;
    const currentElement = this.elementRef.nativeElement;

    if (currentElement.contains(target)) return;

    if (this.overlayRef) {
      const overlayElement = this.overlayRef.overlayElement;
      if (overlayElement && overlayElement.contains(target)) return;
    }

    this.isOpen.set(false);
  }
}
