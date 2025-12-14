import { Component, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { Router, RouterOutlet, ActivatedRoute, NavigationEnd } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map } from 'rxjs';
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
        height: 100vh;
      }

      .organization-layout_container {
        @apply flex;
        @apply flex-1;
        @apply w-full;
        @apply min-h-0;
        @apply h-full;
      }

      .organization-layout_sidebar {
        width: 256px; /* Fixed width: w-64 = 16rem = 256px */
        height: 100vh; /* Fixed height: full viewport height */
        @apply flex-shrink-0;
        @apply border-r;
        @apply border-border-default;
        @apply flex flex-col;
        @apply min-h-0;
      }

      .organization-layout_content {
        @apply flex-1;
        @apply min-w-0;
        @apply overflow-auto;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationLayout {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  readonly navigationService = inject(NavigationService);

  // Make router URL reactive using toSignal
  private readonly currentUrl = toSignal(
    this.router.events.pipe(
      filter((event) => event instanceof NavigationEnd),
      map(() => this.router.url),
    ),
    { initialValue: this.router.url },
  );

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId();
  });

  readonly isProjectsActive = computed(() => {
    const url = this.currentUrl();
    const orgId = this.organizationId();
    if (!orgId) return false;

    // Projects is active when on projects list or any project detail/settings page
    const projectsPattern = `/app/organizations/${orgId}/projects`;
    return url === projectsPattern || url.startsWith(`${projectsPattern}/`);
  });

  readonly isSpacesActive = computed(() => {
    const url = this.currentUrl();
    const orgId = this.organizationId();
    if (!orgId) return false;

    // Spaces is active when on spaces list or any space detail/settings page
    const spacesPattern = `/app/organizations/${orgId}/spaces`;
    return url === spacesPattern || url.startsWith(`${spacesPattern}/`);
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
