import {
  Injectable,
  inject,
  ComponentRef,
  ViewContainerRef,
  ApplicationRef,
  ComponentFactoryResolver,
  EmbeddedViewRef,
} from '@angular/core';
import { Overlay, OverlayRef, OverlayConfig, OverlayPositionBuilder } from '@angular/cdk/overlay';
import { ComponentPortal } from '@angular/cdk/portal';
import { Toast } from './toast';

export type ToastType = 'success' | 'error' | 'warning' | 'info';
export type ToastPosition =
  | 'top-right'
  | 'top-left'
  | 'bottom-right'
  | 'bottom-left'
  | 'top-center'
  | 'bottom-center';

export interface ToastConfig {
  type?: ToastType;
  message: string;
  duration?: number; // in milliseconds, 0 means no auto-dismiss
  position?: ToastPosition;
  closable?: boolean;
}

interface ToastRef {
  overlayRef: OverlayRef;
  componentRef: ComponentRef<Toast>;
  position: ToastPosition;
}

@Injectable({
  providedIn: 'root',
})
export class ToastService {
  private overlay = inject(Overlay);
  private applicationRef = inject(ApplicationRef);
  private toastRefs: Map<string, ToastRef> = new Map();
  private toastCounter = 0;

  show(config: ToastConfig): string {
    const toastId = `toast-${++this.toastCounter}`;
    const position = config.position || 'top-right';
    const duration = config.duration ?? 5000; // Default 5 seconds

    // Count how many toasts are already shown at this position
    const toastsAtPosition = Array.from(this.toastRefs.values()).filter(
      (ref) => ref.position === position,
    );
    const stackIndex = toastsAtPosition.length;
    const toastHeight = 80; // Approximate height of a toast in pixels (including margin)
    const offset = stackIndex * toastHeight;

    const overlayConfig: OverlayConfig = {
      positionStrategy: this.getPositionStrategy(position, offset),
      scrollStrategy: this.overlay.scrollStrategies.noop(),
      hasBackdrop: false,
      panelClass: ['lib-toast-panel', `lib-toast-panel--${position}`],
      disposeOnNavigation: true,
    };

    const overlayRef = this.overlay.create(overlayConfig);

    // Create portal with injector that provides the config
    const portal = new ComponentPortal(Toast);
    const componentRef = overlayRef.attach(portal);

    // Set inputs immediately after attach, before change detection
    componentRef.instance.toastId = toastId;
    componentRef.setInput('type', config.type || 'info');
    componentRef.setInput('message', config.message);
    componentRef.setInput('closable', config.closable !== false);

    // Subscribe to close event
    componentRef.instance.close.subscribe(() => {
      this.close(toastId);
    });

    // Trigger change detection after setting inputs
    componentRef.changeDetectorRef.detectChanges();

    // Auto-dismiss
    if (duration > 0) {
      setTimeout(() => {
        this.close(toastId);
      }, duration);
    }

    this.toastRefs.set(toastId, { overlayRef, componentRef, position });

    return toastId;
  }

  success(message: string, duration?: number): string {
    return this.show({ type: 'success', message, duration });
  }

  error(message: string, duration?: number): string {
    return this.show({ type: 'error', message, duration });
  }

  warning(message: string, duration?: number): string {
    return this.show({ type: 'warning', message, duration });
  }

  info(message: string, duration?: number): string {
    return this.show({ type: 'info', message, duration });
  }

  close(toastId: string): void {
    const toastRef = this.toastRefs.get(toastId);
    if (toastRef) {
      const position = toastRef.position;
      toastRef.overlayRef.dispose();
      this.toastRefs.delete(toastId);

      // Recalculate positions for remaining toasts at the same position
      this.repositionToasts(position);
    }
  }

  private repositionToasts(position: ToastPosition): void {
    const toastsAtPosition = Array.from(this.toastRefs.entries())
      .filter(([_, ref]) => ref.position === position)
      .map(([id, ref]) => ({ id, ref }));

    toastsAtPosition.forEach(({ id, ref }, index) => {
      const toastHeight = 80;
      const offset = index * toastHeight;
      const newStrategy = this.getPositionStrategy(position, offset);
      ref.overlayRef.updatePositionStrategy(newStrategy);
    });
  }

  closeAll(): void {
    this.toastRefs.forEach((_, toastId) => {
      this.close(toastId);
    });
  }

  private getPositionStrategy(position: ToastPosition, offset: number = 0) {
    const positionBuilder = this.overlay.position();
    const globalPosition = positionBuilder.global();
    const topOffset = `calc(1rem + ${offset}px)`;
    const bottomOffset = `calc(1rem + ${offset}px)`;

    switch (position) {
      case 'top-right':
        return globalPosition.top(topOffset).right('1rem');
      case 'top-left':
        return globalPosition.top(topOffset).left('1rem');
      case 'bottom-right':
        return globalPosition.bottom(bottomOffset).right('1rem');
      case 'bottom-left':
        return globalPosition.bottom(bottomOffset).left('1rem');
      case 'top-center':
        return globalPosition.top(topOffset).centerHorizontally();
      case 'bottom-center':
        return globalPosition.bottom(bottomOffset).centerHorizontally();
      default:
        return globalPosition.top(topOffset).right('1rem');
    }
  }
}
