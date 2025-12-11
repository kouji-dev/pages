import { Component, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { Router, RouterOutlet, ActivatedRoute } from '@angular/router';
import { NavigationService } from '../../application/services/navigation.service';
import { BackToPage } from '../components/back-to-page';
import { SidebarNav, SidebarNavItem } from '../components/sidebar-nav';

@Component({
  selector: 'app-organization-layout',
  imports: [RouterOutlet, SidebarNav, BackToPage],
  template: `
    <div class="organization-layout">
      <div class="organization-layout_container">
        <div class="organization-layout_sidebar">
          <app-sidebar-nav [items]="navItems()">
            <div header>
              <app-back-to-page
                label="Back to Organizations"
                (onClick)="handleGoToOrganizations()"
              />
            </div>
          </app-sidebar-nav>
        </div>
        <div class="organization-layout_content">
          <router-outlet />
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .organization-layout {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .organization-layout_container {
        @apply flex;
        @apply flex-1;
        @apply w-full;
        @apply min-h-0;
      }

      .organization-layout_sidebar {
        @apply w-64;
        @apply flex-shrink-0;
        @apply border-r;
        @apply border-border-default;
        @apply flex flex-col;
        @apply h-full;
        @apply min-h-0;
      }

      .organization-layout_content {
        @apply flex-1;
        @apply min-w-0;
        @apply overflow-auto;
      }

      @media (max-width: 768px) {
        .organization-layout_sidebar {
          @apply w-48;
        }
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationLayout {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  readonly navigationService = inject(NavigationService);

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId();
  });

  readonly isProjectsActive = computed(() => {
    const url = this.router.url;
    const orgId = this.organizationId();
    if (!orgId) return false;

    // Check if we're exactly on the projects list route
    // Detail pages will have additional path segments, so exact match works
    const projectsPattern = `/app/organizations/${orgId}/projects`;
    return url === projectsPattern;
  });

  readonly isSpacesActive = computed(() => {
    const url = this.router.url;
    const orgId = this.organizationId();
    if (!orgId) return false;

    // Check if we're exactly on the spaces list route
    // Detail pages will have additional path segments, so exact match works
    const spacesPattern = `/app/organizations/${orgId}/spaces`;
    return url === spacesPattern;
  });

  readonly navItems = computed<SidebarNavItem[]>(() => {
    return [
      {
        label: 'Projects',
        icon: 'folder',
        active: this.isProjectsActive(),
        onClick: () => this.handleNavigateToProjects(),
      },
      {
        label: 'Spaces',
        icon: 'book',
        active: this.isSpacesActive(),
        onClick: () => this.handleNavigateToSpaces(),
      },
    ];
  });

  handleNavigateToProjects(): void {
    const orgId = this.organizationId();
    if (orgId) {
      this.navigationService.navigateToOrganizationProjects(orgId);
    }
  }

  handleNavigateToSpaces(): void {
    const orgId = this.organizationId();
    if (orgId) {
      this.navigationService.navigateToOrganizationSpaces(orgId);
    }
  }

  handleGoToOrganizations(): void {
    this.navigationService.navigateToOrganizations();
  }
}
