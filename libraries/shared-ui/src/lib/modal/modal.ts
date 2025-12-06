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
import { Subject, Observable } from 'rxjs';
import { take } from 'rxjs/operators';

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
  private resultSubject: Subject<any> | null = null;

  open<T = any>(
    content: TemplateRef<any> | Type<any>,
    viewContainerRef: ViewContainerRef,
    config: ModalConfig = {},
  ): Observable<T> {
    if (this.overlayRef) {
      this.close();
    }

    // Create a subject to emit the result when modal closes
    this.resultSubject = new Subject<T>();

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
    } else {
      // Handle component
      portal = new ComponentPortal(content, viewContainerRef);
      const componentRef = this.overlayRef.attach(portal);

      // Pass data to component if it has a data input
      if (config.data) {
        componentRef.setInput('data', config.data);
      }

      this.setupEventHandlers(config);
    }

    // Return observable that completes when modal closes
    return this.resultSubject.asObservable().pipe(take(1));
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

  close<T = any>(payload?: T): void {
    if (this.resultSubject) {
      this.resultSubject.next(payload);
      this.resultSubject.complete();
      this.resultSubject = null;
    }

    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
    }
  }
}
