import {
  Component,
  contentChild,
  ElementRef,
  ChangeDetectionStrategy,
  signal,
  effect,
  DestroyRef,
  inject,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { PageHeader } from '../page-header/page-header';

@Component({
  selector: 'app-page-body',
  imports: [CommonModule],
  template: `
    <div class="page-body" [style.height.px]="bodyHeight()">
      <ng-content select="app-page-header"></ng-content>
      <ng-content select="app-page-content"></ng-content>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .page-body {
        @apply flex flex-col;
        @apply w-full;
        @apply overflow-hidden;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageBody {
  private readonly destroyRef = inject(DestroyRef);
  private readonly elementRef = inject(ElementRef<HTMLElement>);

  headerRef = contentChild(PageHeader, { read: ElementRef });

  readonly bodyHeight = signal<number>(0);
  private resizeObserver?: ResizeObserver;
  private windowResizeHandler?: () => void;

  constructor() {
    effect(() => {
      const headerElement = this.headerRef()?.nativeElement;

      if (!headerElement) {
        // No header - use full viewport height
        this.bodyHeight.set(window.innerHeight);
        this.setupWindowResizeObserver();
        return;
      }

      this.updateHeight(headerElement);
      this.setupResizeObserver(headerElement);
    });
  }

  private updateHeight(header: HTMLElement): void {
    const headerHeight = header.offsetHeight;
    const viewportHeight = window.innerHeight;
    const calculatedHeight = Math.max(0, viewportHeight - headerHeight);

    this.bodyHeight.set(calculatedHeight);
  }

  private setupWindowResizeObserver(): void {
    // Clean up existing handler
    if (this.windowResizeHandler) {
      window.removeEventListener('resize', this.windowResizeHandler);
    }

    // Observe window resize for full-height case
    this.windowResizeHandler = () => {
      this.bodyHeight.set(window.innerHeight);
    };
    window.addEventListener('resize', this.windowResizeHandler);

    this.destroyRef.onDestroy(() => {
      if (this.windowResizeHandler) {
        window.removeEventListener('resize', this.windowResizeHandler);
      }
    });
  }

  private setupResizeObserver(header: HTMLElement): void {
    // Clean up existing observer
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    if (this.windowResizeHandler) {
      window.removeEventListener('resize', this.windowResizeHandler);
    }

    // Create new observer
    this.resizeObserver = new ResizeObserver(() => {
      this.updateHeight(header);
    });

    this.resizeObserver.observe(header);

    // Also observe window resize
    this.windowResizeHandler = () => {
      this.updateHeight(header);
    };
    window.addEventListener('resize', this.windowResizeHandler);

    this.destroyRef.onDestroy(() => {
      this.resizeObserver?.disconnect();
      if (this.windowResizeHandler) {
        window.removeEventListener('resize', this.windowResizeHandler);
      }
    });
  }
}
