import {
  Injectable,
  inject,
  TemplateRef,
  ViewContainerRef,
  ComponentRef,
  Type,
} from '@angular/core';
import { Overlay, OverlayRef, OverlayConfig } from '@angular/cdk/overlay';
import { TemplatePortal, ComponentPortal } from '@angular/cdk/portal';

export interface ModalConfig {
  size?: 'sm' | 'md' | 'lg';
  closable?: boolean;
  data?: any;
}

@Injectable({
  providedIn: 'root',
})
export class Modal {
  private overlay = inject(Overlay);
  private overlayRef: OverlayRef | null = null;

  open(
    content: TemplateRef<any> | Type<any>,
    viewContainerRef: ViewContainerRef,
    config: ModalConfig = {},
  ): ComponentRef<any> | null {
    if (this.overlayRef) {
      this.close();
    }

    const overlayConfig: OverlayConfig = {
      positionStrategy: this.overlay.position().global().centerHorizontally().centerVertically(),
      scrollStrategy: this.overlay.scrollStrategies.block(),
      hasBackdrop: true,
      backdropClass: 'cdk-overlay-dark-backdrop',
      panelClass: `lib-modal-panel--${config.size || 'md'}`,
      disposeOnNavigation: true,
    };

    this.overlayRef = this.overlay.create(overlayConfig);

    let portal: TemplatePortal<any> | ComponentPortal<any>;

    if (content instanceof TemplateRef) {
      // Handle template
      portal = new TemplatePortal(content, viewContainerRef, {
        $implicit: config.data,
      });
      this.overlayRef.attach(portal);
      this.setupEventHandlers(config);
      return null;
    } else {
      // Handle component
      portal = new ComponentPortal(content, viewContainerRef);
      const componentRef = this.overlayRef.attach(portal);

      // Pass data to component if it has a data input
      if (config.data) {
        componentRef.setInput('data', config.data);
      }

      this.setupEventHandlers(config);
      return componentRef;
    }
  }

  private setupEventHandlers(config: ModalConfig) {
    if (!this.overlayRef) return;

    // Handle backdrop clicks
    this.overlayRef.backdropClick().subscribe(() => {
      if (config.closable !== false) {
        this.close();
      }
    });

    // Handle escape key
    this.overlayRef.keydownEvents().subscribe((event) => {
      if (event.key === 'Escape' && config.closable !== false) {
        this.close();
      }
    });
  }

  close(): void {
    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
    }
  }
}
