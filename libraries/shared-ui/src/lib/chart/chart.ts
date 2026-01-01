import {
  Component,
  ChangeDetectionStrategy,
  input,
  effect,
  ElementRef,
  viewChild,
  OnDestroy,
  AfterViewInit,
  NgZone,
  inject,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import * as echarts from 'echarts';
import type { EChartsOption, ECharts } from 'echarts';

/**
 * Chart component that wraps ECharts
 *
 * @example
 * ```html
 * <lib-chart [options]="chartOptions()" [height]="'400px'" />
 * ```
 */
@Component({
  selector: 'lib-chart',
  standalone: true,
  imports: [CommonModule],
  template: ` <div #chartContainer class="chart-container" [style.height]="height()"></div> `,
  styles: [
    `
      @reference "#theme";

      .chart-container {
        @apply w-full;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Chart implements OnDestroy, AfterViewInit {
  private readonly chartContainer = viewChild<ElementRef<HTMLDivElement>>('chartContainer');
  private readonly ngZone = inject(NgZone);
  private chartInstance: ECharts | null = null;
  private resizeObserver: ResizeObserver | null = null;
  private initChartTimer?: number;
  private resizeAnimationFrameId?: number;
  private previousTheme: string | object | undefined = undefined;

  /**
   * ECharts options configuration
   */
  readonly options = input<EChartsOption | null>(null);

  /**
   * Chart height (default: '400px')
   */
  readonly height = input<string>('400px');

  /**
   * Theme name for ECharts
   */
  readonly theme = input<string | object | undefined>(undefined);

  /**
   * Whether to enable responsive resizing (default: true)
   */
  readonly responsive = input<boolean>(true);

  constructor() {
    effect(() => {
      const container = this.chartContainer();
      const opts = this.options();
      const theme = this.theme();

      if (!container?.nativeElement) {
        return;
      }

      // Handle theme changes - need to recreate chart
      if (this.chartInstance && theme !== this.previousTheme) {
        this.refreshChart();
        this.previousTheme = theme;
        return;
      }

      // Handle options changes
      if (opts) {
        this.onOptionsChange(opts);
      } else {
        // Clear chart if options are null/undefined
        this.dispose();
      }
    });
  }

  ngAfterViewInit(): void {
    // Delay initialization to ensure DOM is ready
    this.initChartTimer = window.setTimeout(() => {
      const container = this.chartContainer()?.nativeElement;
      const opts = this.options();

      if (container && opts) {
        this.initChart();
      }
    }, 0);
  }

  ngOnDestroy(): void {
    if (this.initChartTimer) {
      window.clearTimeout(this.initChartTimer);
    }
    if (this.resizeAnimationFrameId) {
      window.cancelAnimationFrame(this.resizeAnimationFrameId);
    }
    this.dispose();
  }

  private dispose(): void {
    if (this.chartInstance) {
      if (!this.chartInstance.isDisposed()) {
        this.chartInstance.dispose();
      }
      this.chartInstance = null;
    }

    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
  }

  /**
   * Refresh chart (dispose and recreate)
   */
  private refreshChart(): void {
    this.dispose();
    this.initChart();
  }

  /**
   * Initialize chart
   */
  private initChart(): void {
    const container = this.chartContainer()?.nativeElement;
    const opts = this.options();
    const theme = this.theme();

    if (!container || !opts) {
      return;
    }

    // Ensure container has dimensions
    this.ensureContainerDimensions(container);

    // Check if container has dimensions, if not, wait
    if (container.clientWidth === 0 || container.clientHeight === 0) {
      requestAnimationFrame(() => {
        if (container.clientWidth > 0 && container.clientHeight > 0) {
          this.createChart(container, opts, theme);
        } else {
          // Try again after a short delay
          setTimeout(() => {
            if (container.clientWidth > 0 && container.clientHeight > 0) {
              this.createChart(container, opts, theme);
            }
          }, 100);
        }
      });
      return;
    }

    this.createChart(container, opts, theme);
  }

  /**
   * Ensure container has dimensions
   */
  private ensureContainerDimensions(container: HTMLDivElement): void {
    if (window && window.getComputedStyle) {
      const computedStyle = window.getComputedStyle(container, null);
      const height = computedStyle.getPropertyValue('height');

      // If no height is set, use the input height or default
      if (
        (!height || height === '0px') &&
        (!container.style.height || container.style.height === '0px')
      ) {
        container.style.height = this.height();
      }
    }
  }

  /**
   * Create chart instance
   */
  private createChart(
    container: HTMLDivElement,
    options: EChartsOption,
    theme?: string | object | undefined,
  ): void {
    // Dispose existing chart
    this.dispose();

    // Create new chart instance outside Angular zone for better performance
    this.ngZone.runOutsideAngular(() => {
      try {
        this.chartInstance = echarts.init(container, theme);
        this.previousTheme = theme;

        // Set options
        this.setOption(options, true);

        // Setup responsive resizing
        if (this.responsive()) {
          this.setupResizeObserver(container);
        }
      } catch (error) {
        console.error('Error initializing chart:', error);
      }
    });
  }

  /**
   * Handle options change
   */
  private onOptionsChange(options: EChartsOption | null): void {
    if (!options) {
      this.dispose();
      return;
    }

    if (this.chartInstance) {
      this.setOption(options, true);
    } else {
      // Chart not initialized yet, initialize it
      this.initChart();
    }
  }

  /**
   * Set chart options with error handling
   */
  private setOption(options: EChartsOption, notMerge?: boolean): void {
    if (this.chartInstance && !this.chartInstance.isDisposed()) {
      try {
        this.chartInstance.setOption(options, notMerge);
      } catch (error) {
        console.error('Error setting chart options:', error);
      }
    }
  }

  /**
   * Setup resize observer with throttling
   */
  private setupResizeObserver(container: HTMLDivElement): void {
    if (!window.ResizeObserver) {
      console.warn('ResizeObserver is not supported');
      return;
    }

    let resizeTimer: number | null = null;

    this.resizeObserver = this.ngZone.runOutsideAngular(
      () =>
        new ResizeObserver(() => {
          // Throttle resize events
          if (resizeTimer) {
            window.cancelAnimationFrame(resizeTimer);
          }

          resizeTimer = window.requestAnimationFrame(() => {
            if (this.chartInstance && !this.chartInstance.isDisposed()) {
              this.chartInstance.resize();
            }
          });
        }),
    );

    this.resizeObserver.observe(container);
  }

  /**
   * Get the ECharts instance (for advanced usage)
   */
  getInstance(): ECharts | null {
    return this.chartInstance;
  }

  /**
   * Resize the chart manually
   */
  resize(): void {
    if (this.chartInstance && !this.chartInstance.isDisposed()) {
      this.chartInstance.resize();
    }
  }
}
