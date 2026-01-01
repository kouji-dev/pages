import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  effect,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  Card,
  Button,
  LoadingState,
  ErrorState,
  Icon,
  Badge,
  Progress,
  type ProgressStatus,
} from 'shared-ui';
import { Chart } from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import {
  SprintService,
  BurndownStatsResponse,
  IssueStatsResponse,
} from '../../../../application/services/sprint.service';
import type { EChartsOption } from 'echarts';

@Component({
  selector: 'app-review-page',
  standalone: true,
  imports: [CommonModule, LoadingState, ErrorState, Icon, Progress, Chart, TranslatePipe],
  template: `
    @if (isLoading()) {
      <lib-loading-state [message]="'review.loading' | translate" />
    } @else if (hasError()) {
      <lib-error-state
        [title]="'review.failedToLoad' | translate"
        [message]="errorMessage()"
        [retryLabel]="'common.retry' | translate"
        (onRetry)="loadStats()"
      />
    } @else {
      <div class="review-page">
        <!-- Stats Cards -->
        <div class="review-page_stats">
          @for (stat of stats(); track stat.title) {
            <div class="review-page_stat-card">
              <div class="review-page_stat-header">
                <span class="review-page_stat-title">{{ stat.title }}</span>
                <lib-icon [name]="stat.icon" [size]="'xs'" [class]="stat.iconClass" />
              </div>
              <div class="review-page_stat-content">
                <div class="review-page_stat-value">{{ stat.value }}</div>
              </div>
            </div>
          }
        </div>

        <!-- Charts with Tabs -->
        <div class="review-page_charts">
          <div class="review-page_tabs">
            <div class="review-page_tabs-list">
              <button
                type="button"
                class="review-page_tabs-trigger"
                [class.review-page_tabs-trigger--active]="activeTab() === 'burndown'"
                (click)="activeTab.set('burndown')"
              >
                <lib-icon name="trending-down" [size]="'xs'" />
                {{ 'review.burndown' | translate }}
              </button>
              <button
                type="button"
                class="review-page_tabs-trigger"
                [class.review-page_tabs-trigger--active]="activeTab() === 'breakdown'"
                (click)="activeTab.set('breakdown')"
              >
                <lib-icon name="activity" [size]="'xs'" />
                {{ 'review.breakdown' | translate }}
              </button>
            </div>

            @if (activeTab() === 'burndown') {
              <div class="review-page_tabs-content">
                <div class="review-page_chart">
                  <div class="review-page_chart-content">
                    <lib-chart [options]="burndownChartOptions() || {}" [height]="'400px'" />
                  </div>
                </div>
              </div>
            }

            @if (activeTab() === 'breakdown') {
              <div class="review-page_tabs-content">
                <div class="review-page_chart">
                  <div class="review-page_chart-content">
                    <div class="review-page_breakdown">
                      @for (breakdown of storyPointsBreakdown(); track breakdown.status) {
                        <div class="review-page_breakdown-item">
                          <div class="review-page_breakdown-header">
                            <span class="review-page_breakdown-label">
                              <span
                                class="review-page_breakdown-indicator"
                                [class]="breakdown.indicatorClass"
                              ></span>
                              {{ breakdown.label }}
                            </span>
                            <span class="review-page_breakdown-value"
                              >{{ breakdown.points }} pts</span
                            >
                          </div>
                          <lib-progress
                            [value]="breakdown.percentage"
                            [status]="breakdown.status"
                          />
                        </div>
                      }
                    </div>
                  </div>
                </div>
              </div>
            }
          </div>
        </div>
      </div>
    }
  `,
  styles: [
    `
      @reference "#mainstyles";

      .review-page {
        @apply flex flex-col;
        @apply gap-6;
        @apply w-full;
      }

      .review-page_stats {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4;
        gap: var(--spacing-4);
      }

      .review-page_stat-card {
        @apply rounded-lg;
        @apply border border-border;
        @apply bg-card;
        @apply text-card-foreground;
        @apply shadow-sm;
        padding: var(--spacing-6);
      }

      .review-page_stat-header {
        @apply flex flex-row items-center justify-between;
        @apply space-y-0;
        padding-bottom: var(--spacing-2);
      }

      .review-page_stat-title {
        font-size: var(--text-sm);
        @apply font-medium;
        color: var(--color-muted-foreground);
      }

      .review-page_stat-content {
        padding-top: 0;
      }

      .review-page_stat-value {
        font-size: var(--text-2xl);
        @apply font-bold;
        color: var(--color-foreground);
      }

      .review-page_charts {
        @apply w-full;
      }

      .review-page_tabs {
        @apply flex flex-col;
        @apply w-full;
        gap: var(--spacing-4);
      }

      .review-page_tabs-list {
        @apply inline-flex items-center justify-start;
        @apply rounded-lg;
        @apply bg-muted;
        @apply p-1;
        @apply text-muted-foreground;
        @apply w-full;
      }

      .review-page_tabs-trigger {
        @apply inline-flex items-center justify-center;
        @apply whitespace-nowrap;
        @apply rounded-md;
        @apply px-3 py-1.5;
        font-size: var(--text-sm);
        @apply font-medium;
        @apply ring-offset-background;
        @apply transition-all;
        @apply focus-visible:outline-none;
        @apply focus-visible:ring-2;
        @apply focus-visible:ring-ring;
        @apply focus-visible:ring-offset-2;
        @apply disabled:pointer-events-none;
        @apply disabled:opacity-50;
        @apply cursor-pointer;
        @apply border-none;
        @apply bg-transparent;
        gap: var(--spacing-2);
        color: var(--color-muted-foreground);
      }

      .review-page_tabs-trigger:hover {
        color: var(--color-foreground);
      }

      .review-page_tabs-trigger--active {
        @apply bg-background;
        @apply shadow-sm;
        color: var(--color-foreground);
      }

      .review-page_tabs-content {
        @apply w-full;
        @apply mt-0;
      }

      .review-page_chart {
        @apply rounded-lg;
        @apply border border-border;
        @apply bg-card;
        @apply text-card-foreground;
        @apply shadow-sm;
        padding: var(--spacing-6);
      }

      .review-page_chart-content {
        @apply w-full;
      }

      .review-page_empty {
        font-size: var(--text-sm);
        color: var(--color-muted-foreground);
        @apply text-center;
        padding-top: var(--spacing-8);
        padding-bottom: var(--spacing-8);
      }

      .review-page_breakdown {
        @apply flex flex-col;
        gap: var(--spacing-4);
      }

      .review-page_breakdown-item {
        @apply flex flex-col;
        gap: var(--spacing-2);
      }

      .review-page_breakdown-header {
        @apply flex items-center justify-between;
        font-size: var(--text-sm);
      }

      .review-page_breakdown-label {
        @apply flex items-center;
        gap: var(--spacing-2);
        color: var(--color-foreground);
      }

      .review-page_breakdown-indicator {
        width: var(--spacing-3);
        height: var(--spacing-3);
        border-radius: var(--radius-full);
      }

      .review-page_breakdown-indicator--todo {
        background-color: var(--color-muted-foreground);
      }

      .review-page_breakdown-indicator--in-progress {
        background-color: var(--color-warning);
      }

      .review-page_breakdown-indicator--done {
        background-color: var(--color-success);
      }

      .review-page_breakdown-value {
        @apply font-medium;
        color: var(--color-foreground);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReviewPage {
  private readonly sprintService = inject(SprintService);
  private readonly translateService = inject(TranslateService);

  readonly isLoading = signal(false);
  readonly hasError = signal(false);
  readonly errorMessage = signal<string>('');

  readonly burndownStats = signal<BurndownStatsResponse | null>(null);
  readonly issueStats = signal<IssueStatsResponse | null>(null);
  readonly activeTab = signal<'burndown' | 'breakdown'>('burndown');

  readonly stats = computed(() => {
    const issueStatsData = this.issueStats();
    if (!issueStatsData) return [];

    return [
      {
        title: this.translateService.instant('review.totalIssues'),
        value: issueStatsData.total_issues,
        icon: 'activity' as const,
        iconClass: 'text-primary',
      },
      {
        title: this.translateService.instant('review.completed'),
        value: issueStatsData.completed_issues,
        icon: 'circle-check' as const,
        iconClass: 'text-success',
      },
      {
        title: this.translateService.instant('review.inProgress'),
        value: issueStatsData.in_progress_issues,
        icon: 'clock' as const,
        iconClass: 'text-warning',
      },
      {
        title: this.translateService.instant('review.toDo'),
        value: issueStatsData.todo_issues,
        icon: 'circle-alert' as const,
        iconClass: 'text-muted-foreground',
      },
    ];
  });

  readonly storyPointsBreakdown = computed(() => {
    const issueStatsData = this.issueStats();
    if (!issueStatsData || issueStatsData.total_story_points === 0) return [];

    const total = issueStatsData.total_story_points;

    return [
      {
        status: 'todo' as ProgressStatus,
        label: this.translateService.instant('issues.status.todo'),
        points: issueStatsData.todo_story_points,
        percentage: (issueStatsData.todo_story_points / total) * 100,
        indicatorClass: 'review-page_breakdown-indicator--todo',
      },
      {
        status: 'in-progress' as ProgressStatus,
        label: this.translateService.instant('issues.status.inProgress'),
        points: issueStatsData.in_progress_story_points,
        percentage: (issueStatsData.in_progress_story_points / total) * 100,
        indicatorClass: 'review-page_breakdown-indicator--in-progress',
      },
      {
        status: 'done' as ProgressStatus,
        label: this.translateService.instant('issues.status.done'),
        points: issueStatsData.completed_story_points,
        percentage: (issueStatsData.completed_story_points / total) * 100,
        indicatorClass: 'review-page_breakdown-indicator--done',
      },
    ];
  });

  /**
   * Resolve CSS variable to actual color value
   * ECharts doesn't support CSS variables, so we need to compute them
   * @param varName - CSS variable name without 'var()' and '--' (e.g., 'color-white' or 'color-gray-200')
   */
  private getComputedColor(varName: string): string {
    if (typeof window === 'undefined' || !window.getComputedStyle) {
      return varName; // Fallback for SSR
    }

    // Add '--' prefix if not present
    const fullVarName = varName.startsWith('--') ? varName : `--${varName}`;
    const computedValue = window
      .getComputedStyle(document.documentElement)
      .getPropertyValue(fullVarName)
      .trim();

    return computedValue || varName;
  }

  readonly burndownChartOptions = computed<EChartsOption | null>(() => {
    const burndownData = this.burndownStats();
    if (!burndownData || burndownData.burndown_data.length === 0) {
      return null;
    }

    // Resolve CSS variables to actual colors
    const white = this.getComputedColor('color-white');
    const gray200 = this.getComputedColor('color-gray-200');
    const gray400 = this.getComputedColor('color-gray-400');
    const gray500 = this.getComputedColor('color-gray-500');
    const gray800 = this.getComputedColor('color-gray-800');
    const blue500 = this.getComputedColor('color-blue-500');

    // Format dates for display (show day number or date)
    const dates = burndownData.burndown_data.map((d, index) => {
      const date = new Date(d.date);
      // Format as "Day X" or use date format
      return `Day ${index + 1}`;
    });
    const ideal = burndownData.burndown_data.map((d) => d.ideal);
    const actual = burndownData.burndown_data.map((d) => d.actual);

    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: white,
        borderColor: gray200,
        borderWidth: 1,
        textStyle: {
          color: gray800,
          fontSize: 12,
        },
        formatter: (params: any) => {
          if (Array.isArray(params)) {
            let result = `<div style="margin-bottom: 4px;">${params[0].axisValue}</div>`;
            params.forEach((param: any) => {
              result += `<div style="margin: 2px 0;">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:${param.color};margin-right:5px;"></span>
                ${param.seriesName}: <strong>${param.value}</strong>
              </div>`;
            });
            return result;
          }
          return '';
        },
      },
      legend: {
        data: [
          this.translateService.instant('review.ideal'),
          this.translateService.instant('review.actual'),
        ],
        textStyle: {
          color: gray800,
          fontSize: 12,
        },
        bottom: 0,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '10%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates,
        axisLine: {
          lineStyle: {
            color: gray200,
          },
        },
        axisLabel: {
          color: gray500,
          fontSize: 11,
        },
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: gray200,
          },
        },
        axisLabel: {
          color: gray500,
          fontSize: 11,
        },
        splitLine: {
          lineStyle: {
            color: gray200,
            type: 'dashed',
            width: 1,
            opacity: 0.5,
          },
        },
      },
      series: [
        {
          name: this.translateService.instant('review.ideal'),
          type: 'line',
          data: ideal,
          smooth: false,
          lineStyle: {
            color: gray400,
            type: 'dashed',
            width: 2,
          },
          itemStyle: {
            color: gray400,
          },
          emphasis: {
            lineStyle: {
              color: gray400,
              width: 2,
            },
            itemStyle: {
              color: gray400,
            },
          },
          symbol: 'none',
          animation: false,
        },
        {
          name: this.translateService.instant('review.actual'),
          type: 'line',
          data: actual,
          smooth: true,
          lineStyle: {
            color: blue500,
            width: 2,
          },
          itemStyle: {
            color: blue500,
          },
          areaStyle: {
            color: blue500,
            opacity: 0.2,
          },
          emphasis: {
            lineStyle: {
              color: blue500,
              width: 3,
            },
            itemStyle: {
              color: blue500,
            },
            areaStyle: {
              color: blue500,
              opacity: 0.3,
            },
          },
          symbol: 'circle',
          symbolSize: 4,
        },
      ],
    };
  });

  constructor() {
    // Load stats when current sprint changes
    effect(() => {
      const currentSprint = this.sprintService.currentSprint();
      if (currentSprint) {
        this.loadStats();
      }
    });
  }

  async loadStats(): Promise<void> {
    const currentSprint = this.sprintService.currentSprint();
    if (!currentSprint) {
      this.hasError.set(true);
      this.errorMessage.set(this.translateService.instant('review.noSprintSelected'));
      return;
    }

    this.isLoading.set(true);
    this.hasError.set(false);
    this.errorMessage.set('');

    try {
      const [burndownStats, issueStats] = await Promise.all([
        this.sprintService.getSprintBurndownStats(currentSprint.id),
        this.sprintService.getSprintIssueStats(currentSprint.id),
      ]);

      console.log('Burndown stats:', burndownStats);
      console.log('Issue stats:', issueStats);

      this.burndownStats.set(burndownStats);
      this.issueStats.set(issueStats);
    } catch (error) {
      console.error('Failed to load sprint stats:', error);
      this.hasError.set(true);
      this.errorMessage.set(
        error instanceof Error
          ? error.message
          : this.translateService.instant('review.failedToLoad'),
      );
    } finally {
      this.isLoading.set(false);
    }
  }
}
