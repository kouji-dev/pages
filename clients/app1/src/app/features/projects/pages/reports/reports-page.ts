import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Card, Icon, Tabs, type TabItem, LoadingState, ErrorState, type IconName } from 'shared-ui';
import { Chart } from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { NavigationService } from '../../../../application/services/navigation.service';
import {
  SprintService,
  VelocityReportResponse,
  CumulativeFlowReportResponse,
  ProjectSummaryStatsResponse,
} from '../../../../application/services/sprint.service';
import type { EChartsOption } from 'echarts';

interface SummaryStat {
  title: string;
  value: string;
  subtitle: string;
  icon: IconName;
  iconClass: string;
}

@Component({
  selector: 'app-reports-page',
  standalone: true,
  imports: [CommonModule, Card, Icon, Tabs, Chart, LoadingState, ErrorState, TranslatePipe],
  template: `
    @if (isLoading()) {
      <lib-loading-state [message]="'reports.loading' | translate" />
    } @else if (hasError()) {
      <lib-error-state
        [title]="'reports.failedToLoad' | translate"
        [message]="errorMessage()"
        [retryLabel]="'common.retry' | translate"
        (onRetry)="loadReports()"
      />
    } @else {
      <div class="reports-page_content">
        <!-- Summary Cards -->
        <div class="reports-page_stats">
          @for (stat of summaryStatsComputed(); track stat.title) {
            <div class="reports-page_stat-card">
              <div class="reports-page_stat-header">
                <span class="reports-page_stat-title">{{ stat.title }}</span>
                <lib-icon [name]="stat.icon" [size]="'xs'" [class]="stat.iconClass" />
              </div>
              <div class="reports-page_stat-content">
                <div class="reports-page_stat-value">{{ stat.value }}</div>
                <p class="reports-page_stat-subtitle">{{ stat.subtitle }}</p>
              </div>
            </div>
          }
        </div>

        <!-- Charts with Tabs -->
        <div class="reports-page_charts">
          <lib-tabs
            [tabs]="chartTabs()"
            [activeTab]="activeTab()"
            variant="pills"
            (tabChange)="handleTabChange($event)"
          >
            @if (activeTab() === 'velocity') {
              <div class="reports-page_chart">
                <lib-card [title]="'reports.velocity.title' | translate">
                  <div class="reports-page_chart-content">
                    <lib-chart [options]="velocityChartOptions()" [height]="'400px'" />
                  </div>
                </lib-card>
              </div>
            }

            @if (activeTab() === 'cumulative') {
              <div class="reports-page_chart">
                <lib-card [title]="'reports.cumulative.title' | translate">
                  <div class="reports-page_chart-content">
                    <lib-chart [options]="cumulativeFlowChartOptions()" [height]="'400px'" />
                  </div>
                </lib-card>
              </div>
            }
          </lib-tabs>
        </div>
      </div>
    }
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply block w-full h-full flex-1 min-h-0;
        @apply flex flex-col;
      }

      .reports-page_content {
        @apply flex flex-col gap-6 h-full min-h-0;
        @apply py-6 px-4 sm:px-6 lg:px-8;
      }

      .reports-page_stats {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4;
        @apply flex-shrink-0;
      }

      .reports-page_stat-card {
        @apply rounded-lg border border-border bg-card p-6;
      }

      .reports-page_stat-header {
        @apply flex items-center justify-between mb-4;
      }

      .reports-page_stat-title {
        @apply text-sm font-medium text-muted-foreground;
      }

      .reports-page_stat-content {
        @apply flex flex-col;
      }

      .reports-page_stat-value {
        @apply text-2xl font-bold text-foreground mb-1;
      }

      .reports-page_stat-subtitle {
        @apply text-xs text-muted-foreground;
        margin: 0;
      }

      .reports-page_charts {
        @apply flex-1 min-h-0;
      }

      .reports-page_chart {
        @apply h-full;
      }

      .reports-page_chart-content {
        @apply w-full;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReportsPage {
  private readonly translateService = inject(TranslateService);
  private readonly navigationService = inject(NavigationService);
  private readonly sprintService = inject(SprintService);

  readonly isLoading = signal(false);
  readonly hasError = signal(false);
  readonly errorMessage = signal<string>('');
  readonly activeTab = signal<'velocity' | 'cumulative'>('velocity');

  // API data
  readonly velocityData = signal<VelocityReportResponse | null>(null);
  readonly cumulativeFlowData = signal<CumulativeFlowReportResponse | null>(null);
  readonly summaryStats = signal<ProjectSummaryStatsResponse | null>(null);

  readonly projectId = computed(() => {
    return this.navigationService.currentProjectId() || '';
  });

  readonly chartTabs = computed<TabItem[]>(() => {
    return [
      {
        label: this.translateService.instant('reports.velocity.label'),
        value: 'velocity',
        icon: 'trending-up',
      },
      {
        label: this.translateService.instant('reports.cumulative.label'),
        value: 'cumulative',
        icon: 'activity',
      },
    ];
  });

  readonly summaryStatsComputed = computed<SummaryStat[]>(() => {
    const stats = this.summaryStats();
    if (!stats) return [];

    return [
      {
        title: this.translateService.instant('reports.avgVelocity'),
        value: `${Math.round(stats.avg_velocity)} pts`,
        subtitle: this.translateService.instant('reports.perSprint'),
        icon: 'trending-up',
        iconClass: 'text-success',
      },
      {
        title: this.translateService.instant('reports.teamMembers'),
        value: `${stats.team_members}`,
        subtitle: this.translateService.instant('reports.activeContributors'),
        icon: 'users',
        iconClass: 'text-primary',
      },
      {
        title: this.translateService.instant('reports.cycleTime'),
        value: `${stats.cycle_time_days.toFixed(1)} days`,
        subtitle: this.translateService.instant('reports.avgPerIssue'),
        icon: 'clock',
        iconClass: 'text-warning',
      },
      {
        title: this.translateService.instant('reports.sprintGoal'),
        value: `${Math.round(stats.sprint_goal_completion)}%`,
        subtitle: this.translateService.instant('reports.completionRate'),
        icon: 'crosshair' as const,
        iconClass: 'text-success',
      },
    ];
  });

  handleTabChange(value: string): void {
    if (value === 'velocity' || value === 'cumulative') {
      this.activeTab.set(value);
    }
  }

  async loadReports(): Promise<void> {
    const projectId = this.projectId();
    if (!projectId) {
      this.hasError.set(true);
      this.errorMessage.set(this.translateService.instant('reports.failedToLoad'));
      return;
    }

    this.isLoading.set(true);
    this.hasError.set(false);
    this.errorMessage.set('');

    try {
      const [velocityData, cumulativeFlowData, summaryStats] = await Promise.all([
        this.sprintService.getProjectVelocity(projectId),
        this.sprintService.getProjectCumulativeFlow(projectId, 7),
        this.sprintService.getProjectSummaryStats(projectId),
      ]);

      this.velocityData.set(velocityData);
      this.cumulativeFlowData.set(cumulativeFlowData);
      this.summaryStats.set(summaryStats);
    } catch (error) {
      console.error('Failed to load reports:', error);
      this.hasError.set(true);
      this.errorMessage.set(
        error instanceof Error
          ? error.message
          : this.translateService.instant('reports.failedToLoad'),
      );
    } finally {
      this.isLoading.set(false);
    }
  }

  /**
   * Resolve CSS variable to actual color value
   */
  private getComputedColor(varName: string): string {
    if (typeof window === 'undefined' || !window.getComputedStyle) {
      return varName;
    }

    const fullVarName = varName.startsWith('--') ? varName : `--${varName}`;
    const computedValue = window
      .getComputedStyle(document.documentElement)
      .getPropertyValue(fullVarName)
      .trim();

    return computedValue || varName;
  }

  readonly velocityChartOptions = computed<EChartsOption>(() => {
    const velocityResponse = this.velocityData();
    if (!velocityResponse || velocityResponse.velocity_data.length === 0) {
      return {
        title: {
          text: this.translateService.instant('reports.noData'),
          left: 'center',
          top: 'middle',
          textStyle: {
            color: this.getComputedColor('color-muted-foreground'),
          },
        },
      };
    }

    const velocityData = velocityResponse.velocity_data;
    const white = this.getComputedColor('color-white');
    const gray200 = this.getComputedColor('color-gray-200');
    const gray400 = this.getComputedColor('color-gray-400');
    const gray500 = this.getComputedColor('color-gray-500');
    const gray800 = this.getComputedColor('color-gray-800');
    const primary = this.getComputedColor('color-primary');
    const mutedForeground = this.getComputedColor('color-muted-foreground');

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
      },
      legend: {
        data: [
          this.translateService.instant('reports.velocity.committed'),
          this.translateService.instant('reports.velocity.completed'),
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
        data: velocityData.map((d) => d.sprint_name),
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
          name: this.translateService.instant('reports.velocity.committed'),
          type: 'bar',
          data: velocityData.map((d) => d.committed),
          itemStyle: {
            color: mutedForeground,
          },
        },
        {
          name: this.translateService.instant('reports.velocity.completed'),
          type: 'bar',
          data: velocityData.map((d) => d.completed),
          itemStyle: {
            color: primary,
          },
        },
      ],
    };
  });

  readonly cumulativeFlowChartOptions = computed<EChartsOption>(() => {
    const flowResponse = this.cumulativeFlowData();
    if (!flowResponse || flowResponse.flow_data.length === 0) {
      return {
        title: {
          text: this.translateService.instant('reports.noData'),
          left: 'center',
          top: 'middle',
          textStyle: {
            color: this.getComputedColor('color-muted-foreground'),
          },
        },
      };
    }

    const flowData = flowResponse.flow_data;
    const white = this.getComputedColor('color-white');
    const gray200 = this.getComputedColor('color-gray-200');
    const gray500 = this.getComputedColor('color-gray-500');
    const gray800 = this.getComputedColor('color-gray-800');
    const mutedForeground = this.getComputedColor('color-muted-foreground');
    const warning = this.getComputedColor('color-warning');
    const success = this.getComputedColor('color-success');

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
      },
      legend: {
        data: [
          this.translateService.instant('issues.status.todo'),
          this.translateService.instant('issues.status.inProgress'),
          this.translateService.instant('issues.status.done'),
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
        data: flowData.map((d) => {
          const date = new Date(d.date);
          return date.toLocaleDateString('en-US', { weekday: 'short' });
        }),
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
          name: this.translateService.instant('issues.status.todo'),
          type: 'line',
          data: flowData.map((d) => d.todo),
          smooth: true,
          lineStyle: {
            color: mutedForeground,
            width: 2,
          },
          itemStyle: {
            color: mutedForeground,
          },
          areaStyle: {
            color: mutedForeground,
            opacity: 0.1,
          },
        },
        {
          name: this.translateService.instant('issues.status.inProgress'),
          type: 'line',
          data: flowData.map((d) => d.in_progress),
          smooth: true,
          lineStyle: {
            color: warning,
            width: 2,
          },
          itemStyle: {
            color: warning,
          },
          areaStyle: {
            color: warning,
            opacity: 0.1,
          },
        },
        {
          name: this.translateService.instant('issues.status.done'),
          type: 'line',
          data: flowData.map((d) => d.done),
          smooth: true,
          lineStyle: {
            color: success,
            width: 2,
          },
          itemStyle: {
            color: success,
          },
          areaStyle: {
            color: success,
            opacity: 0.1,
          },
        },
      ],
    };
  });

  constructor() {
    // Load reports when component initializes
    this.loadReports();
  }
}
