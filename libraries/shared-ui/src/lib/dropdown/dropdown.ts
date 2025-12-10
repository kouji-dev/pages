import {
  Directive,
  ElementRef,
  inject,
  model,
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
  readonly containerClass = input<string>('');
  readonly trigger = input<'click' | 'hover'>('click');
  readonly hoverDelay = input(200);

  // Model signal for two-way binding
  readonly open = model(false);

  private overlayRef: OverlayRef | null = null;
  private hoverTimer: number | null = null;

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

  // Effect to sync open state with overlay
  private readonly syncOpenState = effect(() => {
    const isOpen = this.open();
    if (isOpen && !this.overlayRef) {
      this.openOverlay();
    } else if (!isOpen && this.overlayRef) {
      this.closeOverlay();
    }
  });

  constructor() {
    // Register cleanup
    this.destroyRef.onDestroy(() => {
      this.open.set(false);
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
    if (!this.open()) {
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
      this.open.set(false);
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
    this.open.set(false);
  }

  toggle(): void {
    this.open.update((value) => !value);
  }

  private openOverlay(): void {
    if (!this.libDropdown()) {
      return;
    }

    const panelClasses = [this.panelClass()];
    const containerClass = this.containerClass();
    if (containerClass) {
      panelClasses.push(containerClass);
    }

    const config: OverlayConfig = {
      positionStrategy: this.getPositionStrategy(),
      scrollStrategy: this.overlay.scrollStrategies.close(),
      panelClass: panelClasses,
      backdropClass: 'cdk-overlay-transparent-backdrop',
      hasBackdrop: true,
      disposeOnNavigation: true,
    };

    this.overlayRef = this.overlay.create(config);

    const portal = new TemplatePortal(this.libDropdown() as any, this.viewContainerRef as any, {
      $implicit: this.dropdownData(),
    });

    this.overlayRef.attach(portal);

    // Handle backdrop clicks
    this.overlayRef.backdropClick().subscribe(() => {
      this.open.set(false);
    });

    // Handle escape key
    this.overlayRef.keydownEvents().subscribe((event) => {
      if (event.key === 'Escape') {
        this.open.set(false);
      }
    });
  }

  private closeOverlay(): void {
    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
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
      this.open.set(true);
    }, this.hoverDelay());
  }

  private onMouseLeave(): void {
    this.clearHoverTimer();
    this.hoverTimer = window.setTimeout(() => {
      this.open.set(false);
    }, this.hoverDelay());
  }

  private clearHoverTimer(): void {
    if (this.hoverTimer) {
      clearTimeout(this.hoverTimer);
      this.hoverTimer = null;
    }
  }
}
