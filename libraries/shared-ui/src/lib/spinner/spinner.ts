import {
  Directive,
  TemplateRef,
  ViewContainerRef,
  ComponentRef,
  DestroyRef,
  ChangeDetectorRef,
  EmbeddedViewRef,
  Renderer2,
  Injector,
  afterRenderEffect,
  input,
  effect,
  inject,
} from '@angular/core';
import { SpinnerContent, SpinnerSize, SpinnerColor } from './spinner-content';

@Directive({
  selector: '[spinner]',
})
export class Spinner {
  private embeddedViewRef: EmbeddedViewRef<any> | null = null;
  private spinnerComponentRef: ComponentRef<SpinnerContent> | null = null;
  private hostElement: HTMLElement | null = null;
  private isInitialized = false;

  // Inject dependencies using inject()
  private readonly templateRef = inject(TemplateRef<any>);
  private readonly viewContainer = inject(ViewContainerRef);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly renderer = inject(Renderer2);
  private readonly injector = inject(Injector);
  private readonly destroyRef = inject(DestroyRef);

  // Main input for loading state - using signal-based input
  spinner = input<boolean | null | undefined>(false);

  // Optional configuration inputs - using signal-based inputs
  spinnerSize = input<SpinnerSize>('md');
  spinnerColor = input<SpinnerColor>('default');
  spinnerMessage = input<string>('');
  spinnerAriaLabel = input<string>('');

  // Effect to watch for loading state changes
  private readonly updateSpinner = effect(() => {
    const isLoading = Boolean(this.spinner());
    // Only update if already initialized
    if (this.isInitialized) {
      this.updateView(isLoading);
    }
  });

  // Effect to watch for configuration changes (size, color, message, etc.)
  // Explicitly read all input signals so the effect tracks them
  private readonly updateSpinnerConfig = effect(() => {
    // Read all inputs to track changes
    this.spinnerSize();
    this.spinnerColor();
    this.spinnerMessage();
    this.spinnerAriaLabel();

    // If spinner is currently shown, update its configuration
    if (this.spinnerComponentRef && this.isInitialized) {
      this.updateSpinnerComponentInputs();
    }
  });

  private updateSpinnerComponentInputs(): void {
    if (!this.spinnerComponentRef) {
      return;
    }

    // Update all inputs
    this.spinnerComponentRef.setInput('size', this.spinnerSize());
    this.spinnerComponentRef.setInput('color', this.spinnerColor());
    this.spinnerComponentRef.setInput('message', this.spinnerMessage());
    this.spinnerComponentRef.setInput('ariaLabel', this.spinnerAriaLabel() || 'Loading');
    this.spinnerComponentRef.changeDetectorRef.detectChanges();
  }

  // Use afterRenderEffect for DOM manipulation after render
  // Guard against multiple initializations
  private readonly initializeHostElement = afterRenderEffect(() => {
    // Only initialize once
    if (this.isInitialized || this.embeddedViewRef) {
      return;
    }

    // Render the content template
    this.embeddedViewRef = this.viewContainer.createEmbeddedView(this.templateRef);

    // Find the first root node from the embedded view (the actual DOM element)
    if (this.embeddedViewRef.rootNodes.length > 0) {
      this.hostElement = this.embeddedViewRef.rootNodes[0] as HTMLElement;

      // Ensure the host element has position: relative if it doesn't already have a position
      const computedStyle = window.getComputedStyle(this.hostElement);
      if (computedStyle.position === 'static') {
        this.renderer.setStyle(this.hostElement, 'position', 'relative');
      }
    }

    // Mark as initialized and do initial update
    this.isInitialized = true;
    this.updateView(Boolean(this.spinner()));
  });

  constructor() {
    // Register cleanup on destroy
    this.destroyRef.onDestroy(() => {
      this.destroySpinner();
      if (this.embeddedViewRef) {
        this.embeddedViewRef.destroy();
        this.embeddedViewRef = null;
      }
      this.isInitialized = false;
    });
  }

  private updateView(isLoading: boolean): void {
    if (!this.isInitialized || !this.hostElement) {
      return; // Not ready yet
    }

    if (isLoading) {
      this.createSpinner();
    } else {
      this.destroySpinner();
    }
    this.cdr.markForCheck();
  }

  private createSpinner(): void {
    if (this.spinnerComponentRef || !this.hostElement) {
      return; // Already exists or no host element
    }

    // Create spinner component
    this.spinnerComponentRef = this.viewContainer.createComponent(SpinnerContent, {
      injector: this.injector,
    });

    // Set inputs using signal values (will be kept in sync via updateSpinnerConfig effect)
    this.updateSpinnerComponentInputs();

    // Append spinner directly to the host element
    const spinnerElement = this.spinnerComponentRef.location.nativeElement;
    this.renderer.appendChild(this.hostElement, spinnerElement);

    this.spinnerComponentRef.changeDetectorRef.detectChanges();
  }

  private destroySpinner(): void {
    if (this.spinnerComponentRef && this.hostElement) {
      const spinnerElement = this.spinnerComponentRef.location.nativeElement;
      if (spinnerElement.parentNode === this.hostElement) {
        this.renderer.removeChild(this.hostElement, spinnerElement);
      }
      this.spinnerComponentRef.destroy();
      this.spinnerComponentRef = null;
    }
  }
}
