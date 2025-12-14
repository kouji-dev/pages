import {
  Component,
  ChangeDetectionStrategy,
  signal,
  inject,
  effect,
  computed,
  HostListener,
  ViewChild,
  ElementRef,
  OnDestroy,
  TemplateRef,
  ViewContainerRef,
} from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Overlay, OverlayRef, OverlayConfig } from '@angular/cdk/overlay';
import { TemplatePortal } from '@angular/cdk/portal';
import { TranslateModule, TranslatePipe, TranslateService } from '@ngx-translate/core';
import { Input, Icon } from 'shared-ui';
import type { Input as InputComponent } from 'shared-ui';
import { SearchService } from '../../application/services/search.service';
import { NavigationService } from '../../application/services/navigation.service';
import { SearchDropdown } from './search-dropdown';

@Component({
  selector: 'app-search-bar',
  imports: [Input, Icon, FormsModule, SearchDropdown, TranslateModule, TranslatePipe],
  template: `
    <div class="search-bar" #searchBarContainer>
      <lib-input
        #searchInput
        type="search"
        [(model)]="query"
        [placeholder]="computedPlaceholder()"
        leftIcon="search"
        [readonly]="readonly()"
        (keydown.enter)="handleSearch()"
        (focus)="handleFocus()"
        (blur)="handleBlur()"
        (click)="handleClick()"
        (input)="handleInput()"
        class="search-bar_input"
      />
      @if (showKeyboardHint()) {
        <div class="search-bar_hint">
          <kbd class="search-bar_kbd">{{ isMac() ? '⌘' : 'Ctrl' }}</kbd>
          <span class="search-bar_hint-text">+</span>
          <kbd class="search-bar_kbd">K</kbd>
        </div>
      }
    </div>

    <!-- Dropdown Template -->
    <ng-template #dropdownTemplate>
      <app-search-dropdown [query]="query()" />
    </ng-template>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .search-bar {
        @apply relative w-full;
        @apply flex items-center;
        /* No max-width constraint - takes full width of container */
      }

      .search-bar_input {
        @apply w-full;
      }

      .search-bar_input ::ng-deep .input {
        @apply py-3;
        @apply text-lg;
        min-height: 3rem;
      }

      .search-bar_hint {
        @apply absolute right-3;
        @apply flex items-center gap-1;
        @apply pointer-events-none;
        @apply hidden lg:flex;
      }

      .search-bar_kbd {
        @apply px-1.5 py-0.5;
        @apply text-xs;
        @apply font-mono;
        @apply bg-bg-secondary;
        @apply border border-border-default;
        @apply rounded;
        @apply text-text-secondary;
        @apply shadow-sm;
      }

      .search-bar_hint-text {
        @apply text-xs;
        @apply text-text-tertiary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SearchBar implements OnDestroy {
  private readonly router = inject(Router);
  private readonly searchService = inject(SearchService);
  private readonly navigationService = inject(NavigationService);
  private readonly overlay = inject(Overlay);
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  @ViewChild('searchInput', { static: false }) searchInput?: InputComponent;
  @ViewChild('searchBarContainer', { static: false })
  searchBarContainer?: ElementRef<HTMLDivElement>;
  @ViewChild('dropdownTemplate', { static: false }) dropdownTemplate?: TemplateRef<any>;

  readonly placeholder = signal<string>('');

  readonly computedPlaceholder = computed(() => {
    return this.placeholder() || this.translateService.instant('search.placeholder');
  });
  readonly readonly = signal<boolean>(false);
  readonly showKeyboardHint = signal<boolean>(true);
  readonly isDropdownOpen = signal<boolean>(false);

  query = signal<string>('');
  private overlayRef: OverlayRef | null = null;

  // Detect Mac for keyboard shortcut display
  readonly isMac = signal<boolean>(false);

  constructor() {
    // Initialize Mac detection
    if (typeof window !== 'undefined') {
      this.isMac.set(/Mac|iPhone|iPod|iPad/i.test(navigator.platform));
    }

    // Hide keyboard hint when query is not empty
    effect(() => {
      const q = this.query();
      this.showKeyboardHint.set(!q || q.trim().length === 0);
    });

    // Open dropdown when query changes and has content
    effect(() => {
      const q = this.query();
      if (q && q.trim().length > 0) {
        // Small delay to ensure view is updated
        setTimeout(() => {
          this.openDropdown();
        }, 0);
      }
    });
  }

  // Keyboard shortcut handler - use document level to catch all events
  @HostListener('document:keydown', ['$event'])
  handleKeyDown(event: KeyboardEvent): void {
    // Skip if user is typing in an input/textarea
    const target = event.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      return;
    }

    // Cmd+K (Mac) or Ctrl+K (Windows/Linux)
    const isMac = this.isMac();
    const isModifierPressed = isMac ? event.metaKey : event.ctrlKey;
    const isKPressed = event.key === 'k' || event.key === 'K';

    if (isModifierPressed && isKPressed) {
      event.preventDefault();
      event.stopPropagation();
      this.focusSearch();
    }
  }

  ngOnDestroy(): void {
    this.closeDropdown();
  }

  handleSearch(): void {
    const query = this.query().trim();
    if (!query) return;

    // Close dropdown when Enter is pressed
    this.closeDropdown();
  }

  handleClick(): void {
    // Open dropdown when clicking on the input
    this.openDropdown();
  }

  handleFocus(): void {
    // Always show dropdown when focused, even if empty
    this.openDropdown();
  }

  handleBlur(): void {
    // Delay closing to allow clicks on dropdown items
    setTimeout(() => {
      if (!this.isDropdownOpen()) return;
      // Check if focus moved to dropdown
      const activeElement = document.activeElement;
      if (activeElement && this.overlayRef?.overlayElement.contains(activeElement)) {
        return;
      }
      this.closeDropdown();
    }, 200);
  }

  handleInput(): void {
    // Query is already updated via two-way binding
    // Dropdown will open/close via effect watching query signal
  }

  private openDropdown(): void {
    if (this.isDropdownOpen() || !this.dropdownTemplate || !this.searchBarContainer) {
      return;
    }

    const config: OverlayConfig = {
      positionStrategy: this.overlay
        .position()
        .flexibleConnectedTo(this.searchBarContainer.nativeElement)
        .withPositions([
          {
            originX: 'start',
            originY: 'bottom',
            overlayX: 'start',
            overlayY: 'top',
            offsetY: 8,
          },
        ])
        .withFlexibleDimensions(true)
        .withPush(true),
      scrollStrategy: this.overlay.scrollStrategies.reposition(),
      panelClass: 'search-dropdown-overlay',
      backdropClass: 'cdk-overlay-transparent-backdrop',
      hasBackdrop: true,
      disposeOnNavigation: true,
    };

    this.overlayRef = this.overlay.create(config);
    const portal = new TemplatePortal(this.dropdownTemplate, this.viewContainerRef);
    this.overlayRef.attach(portal);
    this.isDropdownOpen.set(true);

    // Handle backdrop clicks
    this.overlayRef.backdropClick().subscribe(() => {
      this.closeDropdown();
    });

    // Handle escape key
    this.overlayRef.keydownEvents().subscribe((event) => {
      if (event.key === 'Escape') {
        this.closeDropdown();
        // Refocus search input
        this.focusSearch();
      }
    });
  }

  private closeDropdown(): void {
    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
    }
    this.isDropdownOpen.set(false);
  }

  focusSearch(): void {
    // Focus the search input - access the native input element
    if (this.searchInput) {
      // Use setTimeout to ensure the view is updated
      setTimeout(() => {
        const inputElement = document.querySelector('.search-bar_input input') as HTMLInputElement;
        if (inputElement) {
          inputElement.focus();
          inputElement.select();
        }
      }, 0);
    }
  }
}
