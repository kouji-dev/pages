import { Component, ChangeDetectionStrategy, input, computed, inject } from '@angular/core';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { Tabs, type TabItem } from 'shared-ui';
import { TranslateService } from '@ngx-translate/core';
import { NavigationService } from '../../../../application/services/navigation.service';

@Component({
  selector: 'app-project-nav',
  standalone: true,
  imports: [Tabs],
  template: `
    <lib-tabs
      [tabs]="navTabs()"
      [activeTab]="currentTab()"
      variant="default"
      [showContent]="false"
    />
  `,
  styles: [
    `
      @reference "#mainstyles";
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectNav {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly translateService = inject(TranslateService);
  private readonly navigationService = inject(NavigationService);

  readonly projectId = input.required<string>();

  readonly basePath = computed(() => {
    const orgId = this.navigationService.currentOrganizationId();
    const projId = this.projectId();
    if (!orgId || !projId) return '';
    return `/app/organizations/${orgId}/projects/${projId}`;
  });

  readonly queryParams = toSignal(this.route.queryParams, {
    initialValue: {} as Record<string, string>,
  });

  readonly currentTab = computed(() => {
    return this.queryParams()?.['tab'] || 'board';
  });

  readonly navTabs = computed<TabItem[]>(() => {
    const basePath = this.basePath();
    return [
      {
        label: this.translateService.instant('board.title'),
        value: 'board',
        icon: 'columns-2',
        routerLink: basePath,
        queryParams: { tab: 'board' },
      },
      {
        label: this.translateService.instant('review.title'),
        value: 'review',
        icon: 'zap',
        routerLink: basePath,
        queryParams: { tab: 'review' },
      },
      {
        label: this.translateService.instant('sprints.planning'),
        value: 'planning',
        icon: 'list-todo',
        routerLink: basePath,
        queryParams: { tab: 'planning' },
      },
      {
        label: this.translateService.instant('backlog.title'),
        value: 'backlog',
        icon: 'list-todo',
        routerLink: basePath,
        queryParams: { tab: 'backlog' },
      },
      {
        label: this.translateService.instant('reports.title'),
        value: 'reports',
        icon: 'activity',
        routerLink: basePath,
        queryParams: { tab: 'reports' },
      },
    ];
  });
}
