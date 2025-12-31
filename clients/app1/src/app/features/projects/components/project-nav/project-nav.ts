import { Component, ChangeDetectionStrategy, input, computed, inject } from '@angular/core';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { Icon } from 'shared-ui';
import type { IconName } from 'shared-ui';
import { TranslateService } from '@ngx-translate/core';
import { NavigationService } from '../../../../application/services/navigation.service';

interface NavItem {
  label: string;
  tab: string;
  icon: IconName;
}

@Component({
  selector: 'app-project-nav',
  standalone: true,
  imports: [Icon, RouterLink],
  template: `
    <nav class="project-nav">
      @for (item of navItems(); track item.tab) {
        <a
          [routerLink]="basePath()"
          [queryParams]="{ tab: item.tab }"
          [class.project-nav_item]="true"
          [class.project-nav_item--active]="isActive(item.tab)"
        >
          <lib-icon [name]="item.icon" [size]="'sm'" />
          <span>{{ item.label }}</span>
        </a>
      }
    </nav>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .project-nav {
        @apply flex items-center;
        @apply gap-1;
        @apply border-b;
        @apply border-border;
        @apply mb-0;
      }

      .project-nav_item {
        @apply flex items-center;
        @apply gap-2;
        @apply px-4 py-2.5;
        @apply text-sm font-medium;
        @apply border-b-2;
        @apply -mb-px;
        @apply transition-colors;
        @apply text-muted-foreground;
        @apply border-transparent;
        @apply no-underline;
        @apply cursor-pointer;
      }

      .project-nav_item:hover {
        @apply text-foreground;
        @apply border-muted;
      }

      .project-nav_item--active {
        @apply border-primary;
        @apply text-foreground;
      }
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

  readonly navItems = computed<NavItem[]>(() => {
    return [
      {
        label: this.translateService.instant('board.title'),
        tab: 'board',
        icon: 'columns-2',
      },
      {
        label: this.translateService.instant('review.title'),
        tab: 'review',
        icon: 'zap',
      },
      {
        label: this.translateService.instant('sprints.planning'),
        tab: 'planning',
        icon: 'list-todo',
      },
      {
        label: this.translateService.instant('backlog.title'),
        tab: 'backlog',
        icon: 'list-todo',
      },
      {
        label: this.translateService.instant('reports.title'),
        tab: 'reports',
        icon: 'activity',
      },
    ];
  });

  isActive(tab: string): boolean {
    const currentTab = this.queryParams()?.['tab'] || 'board';
    return currentTab === tab;
  }
}
