import {
  Directive,
  ElementRef,
  Output,
  EventEmitter,
  inject,
  signal,
  effect,
  afterRenderEffect,
  input,
  TemplateRef,
  ViewContainerRef,
  HostListener,
  DestroyRef,
} from '@angular/core';
import { Overlay, OverlayRef, OverlayConfig } from '@angular/cdk/overlay';
import { TemplatePortal } from '@angular/cdk/portal';
import { ConnectedPosition } from '@angular/cdk/overlay';

export type DropdownPosition = 'above' | 'below' | 'left' | 'right';

@Directive({
  selector: '[libDropdown]',
  exportAs: 'libDropdown',
})
export class Dropdown {
  private readonly overlay = inject(Overlay);
  private readonly elementRef = inject(ElementRef);
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly libDropdown = input.required<TemplateRef<any>>();
  readonly dropdownData = input<any>();
  readonly position = input<DropdownPosition>('below');
  readonly panelClass = input('lib-dropdown-panel');
  readonly trigger = input<'click' | 'hover'>('click');
  readonly hoverDelay = input(200);

  @Output() dropdownOpened = new EventEmitter<void>();
  @Output() dropdownClosed = new EventEmitter<void>();

  private overlayRef: OverlayRef | null = null;
  private readonly isOpen = signal(false);
  private hoverTimer: number | null = null;

  readonly isDropdownOpen = this.isOpen.asReadonly();

  // Setup event listeners after render
  private readonly setupEventListeners = afterRenderEffect(() => {
    const element = this.elementRef.nativeElement;

    if (this.trigger() === 'click') {
      element.addEventListener('click', this.onElementClick.bind(this));
    } else if (this.trigger() === 'hover') {
      element.addEventListener('mouseenter', this.onMouseEnter.bind(this));
      element.addEventListener('mouseleave', this.onMouseLeave.bind(this));
    }
  });

  constructor() {
    // Register cleanup
    this.destroyRef.onDestroy(() => {
      this.close();
      this.clearHoverTimer();
      const element = this.elementRef.nativeElement;

      if (this.trigger() === 'click') {
        element.removeEventListener('click', this.onElementClick.bind(this));
      } else if (this.trigger() === 'hover') {
        element.removeEventListener('mouseenter', this.onMouseEnter.bind(this));
        element.removeEventListener('mouseleave', this.onMouseLeave.bind(this));
      }
    });
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    if (!this.isOpen()) {
      return;
    }

    const target = event.target as Element;
    const currentElement = this.elementRef.nativeElement;

    // Don't close if clicking on this dropdown trigger or its children
    if (currentElement.contains(target)) {
      return;
    }

    // Don't close if clicking on another dropdown trigger (allow switching between dropdowns)
    const isAnotherDropdownTrigger = target.closest('[libDropdown]');
    if (isAnotherDropdownTrigger && isAnotherDropdownTrigger !== currentElement) {
      // Close this dropdown to allow the other one to open
      this.close();
      return;
    }

    // Don't close if clicking inside the dropdown panel
    if (this.overlayRef) {
      const overlayElement = this.overlayRef.overlayElement;
      if (overlayElement && overlayElement.contains(target)) {
        return;
      }
    }

    // Close the dropdown for any other clicks
    this.close();
  }

  toggle(): void {
    if (this.isOpen()) {
      this.close();
    } else {
      this.open();
    }
  }

  open(): void {
    if (this.isOpen() || !this.libDropdown()) {
      return;
    }

    const config: OverlayConfig = {
      positionStrategy: this.getPositionStrategy(),
      scrollStrategy: this.overlay.scrollStrategies.close(),
      panelClass: this.panelClass(),
      backdropClass: 'cdk-overlay-transparent-backdrop',
      hasBackdrop: true,
      disposeOnNavigation: true,
    };

    this.overlayRef = this.overlay.create(config);

    const portal = new TemplatePortal(this.libDropdown() as any, this.viewContainerRef as any, {
      $implicit: this.dropdownData(),
    });

    this.overlayRef.attach(portal);
    this.isOpen.set(true);
    this.dropdownOpened.emit();

    // Handle backdrop clicks
    this.overlayRef.backdropClick().subscribe(() => {
      this.close();
    });

    // Handle escape key
    this.overlayRef.keydownEvents().subscribe((event) => {
      if (event.key === 'Escape') {
        this.close();
      }
    });
  }

  close(): void {
    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
      this.isOpen.set(false);
      this.dropdownClosed.emit();
    }
  }

  private getPositionStrategy() {
    const positions = this.getConnectedPositions();
    return this.overlay.position().flexibleConnectedTo(this.elementRef).withPositions(positions);
  }

  private getConnectedPositions(): ConnectedPosition[] {
    const position = this.position();

    switch (position) {
      case 'above':
        return [
          { originX: 'center', originY: 'top', overlayX: 'center', overlayY: 'bottom' },
          { originX: 'center', originY: 'bottom', overlayX: 'center', overlayY: 'top' },
        ];
      case 'below':
        return [
          { originX: 'center', originY: 'bottom', overlayX: 'center', overlayY: 'top' },
          { originX: 'center', originY: 'top', overlayX: 'center', overlayY: 'bottom' },
        ];
      case 'left':
        return [
          { originX: 'start', originY: 'center', overlayX: 'end', overlayY: 'center' },
          { originX: 'end', originY: 'center', overlayX: 'start', overlayY: 'center' },
        ];
      case 'right':
        return [
          { originX: 'end', originY: 'center', overlayX: 'start', overlayY: 'center' },
          { originX: 'start', originY: 'center', overlayX: 'end', overlayY: 'center' },
        ];
      default:
        return [{ originX: 'center', originY: 'bottom', overlayX: 'center', overlayY: 'top' }];
    }
  }

  private onElementClick(event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.toggle();
  }

  private onMouseEnter(): void {
    this.clearHoverTimer();
    this.hoverTimer = window.setTimeout(() => {
      this.open();
    }, this.hoverDelay());
  }

  private onMouseLeave(): void {
    this.clearHoverTimer();
    this.hoverTimer = window.setTimeout(() => {
      this.close();
    }, this.hoverDelay());
  }

  private clearHoverTimer(): void {
    if (this.hoverTimer) {
      clearTimeout(this.hoverTimer);
      this.hoverTimer = null;
    }
  }
}
