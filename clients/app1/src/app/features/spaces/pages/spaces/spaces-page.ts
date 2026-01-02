import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  ViewContainerRef,
  signal,
} from '@angular/core';
import { Pagination } from 'shared-ui';
import {
  LoadingState,
  ErrorState,
  EmptyState,
  Modal,
  Input,
  Select,
  SelectOption,
} from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { SpaceService, Space } from '../../../../application/services/space.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { SpaceCard } from '../../components/space-card/space-card';
import { CreateSpaceModal } from '../../components/create-space-modal/create-space-modal';
import {
  PageHeader,
  PageHeaderAction,
  PageHeaderSearchInput,
  PageHeaderFilter,
} from '../../../../shared/layout/page-header/page-header';
import { PageBody } from '../../../../shared/layout/page-body/page-body';
import { PageContent } from '../../../../shared/layout/page-content/page-content';
import { PageFooter } from '../../../../shared/layout/page-footer/page-footer';

@Component({
  selector: 'app-spaces-page',
  imports: [
    LoadingState,
    ErrorState,
    EmptyState,
    SpaceCard,
    Pagination,
    TranslatePipe,
    PageHeader,
    PageBody,
    PageContent,
    PageFooter,
  ],
  template: `
    <app-page-body>
      <app-page-header
        title="spaces.title"
        subtitle="spaces.subtitle"
        [searchInput]="searchInputConfig()"
        [filters]="filtersConfig()"
        [action]="createSpaceAction()"
      />

      <app-page-content>
        @if (!organizationId()) {
          <lib-empty-state
            [title]="'spaces.noOrganizationSelected' | translate"
            [message]="'spaces.noOrganizationSelectedDescription' | translate"
            icon="building"
            [actionLabel]="'spaces.goToOrganizations' | translate"
            actionIcon="arrow-right"
            (onAction)="handleGoToOrganizations()"
          />
        } @else if (spaceService.isLoading()) {
          <lib-loading-state [message]="'spaces.loadingSpaces' | translate" />
        } @else if (spaceService.hasError()) {
          <lib-error-state
            [title]="'spaces.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else {
          <!-- Grid -->
          @if (filteredSpaces().length === 0 && allSpaces().length > 0) {
            <lib-empty-state
              [title]="'spaces.noSpacesFound' | translate"
              [message]="'spaces.noSpacesFoundDescription' | translate"
              icon="search"
            />
          } @else if (filteredSpaces().length === 0) {
            <lib-empty-state
              [title]="'spaces.noSpaces' | translate"
              [message]="'spaces.noSpacesDescription' | translate"
              icon="book"
              [actionLabel]="'spaces.createSpace' | translate"
              actionIcon="plus"
              (onAction)="handleCreateSpace()"
            />
          } @else {
            <div class="spaces-page_grid">
              @for (space of paginatedSpaces(); track space.id) {
                <app-space-card [space]="space" (onSettings)="handleSpaceSettings($event)" />
              }
            </div>
          }
        }
      </app-page-content>

      @if (
        organizationId() &&
        !spaceService.isLoading() &&
        !spaceService.hasError() &&
        filteredSpaces().length > 0
      ) {
        <app-page-footer>
          <lib-pagination
            [currentPage]="currentPage()"
            [totalItems]="filteredSpaces().length"
            [itemsPerPage]="ITEMS_PER_PAGE"
            itemLabel="documents"
            (pageChange)="goToPage($event)"
          />
        </app-page-footer>
      }
    </app-page-body>
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply flex flex-col flex-auto;
        @apply w-full;
        @apply min-h-0;
      }

      .spaces-page_grid {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
        @apply flex-1;
        @apply content-start;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SpacesPage {
  readonly spaceService = inject(SpaceService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  readonly translateService = inject(TranslateService);

  readonly statusFilter = signal<string>('all');
  readonly currentPage = signal<number>(1);
  readonly ITEMS_PER_PAGE = 6;

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId();
  });

  readonly allSpaces = computed(() => {
    const orgId = this.organizationId();
    if (!orgId) return [];
    return this.spaceService.getSpacesByOrganization(orgId);
  });

  readonly statusFilterOptions = computed<SelectOption<string>[]>(() => [
    { value: 'all', label: 'All' },
    { value: 'draft', label: 'Draft' },
    { value: 'in-review', label: 'In Review' },
    { value: 'published', label: 'Published' },
  ]);

  readonly filteredSpaces = computed(() => {
    const spaces = this.allSpaces();
    const query = this.spaceService.searchQuery().toLowerCase().trim();
    const status = this.statusFilter();

    let filtered = spaces;

    // Filter by search query
    if (query) {
      filtered = filtered.filter((space) => {
        const nameMatch = space.name.toLowerCase().includes(query);
        const keyMatch = space.key.toLowerCase().includes(query);
        const descriptionMatch = space.description?.toLowerCase().includes(query) || false;
        return nameMatch || keyMatch || descriptionMatch;
      });
    }

    // Filter by status
    if (status !== 'all') {
      filtered = filtered.filter((space) => space.status === status);
    }

    return filtered;
  });

  readonly totalPages = computed(() => {
    return Math.ceil(this.filteredSpaces().length / this.ITEMS_PER_PAGE);
  });

  readonly paginatedSpaces = computed(() => {
    const spaces = this.filteredSpaces();
    const start = (this.currentPage() - 1) * this.ITEMS_PER_PAGE;
    const end = start + this.ITEMS_PER_PAGE;
    return spaces.slice(start, end);
  });

  readonly errorMessage = computed(() => {
    const error = this.spaceService.error();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading spaces.';
    }
    return 'An unknown error occurred.';
  });

  readonly createSpaceAction = computed<PageHeaderAction>(() => ({
    label: this.translateService.instant('spaces.createSpace'),
    icon: 'plus',
    variant: 'primary',
    size: 'md',
    disabled: !this.organizationId(),
    onClick: () => this.handleCreateSpace(),
  }));

  readonly searchInputConfig = computed<PageHeaderSearchInput | null>(() => {
    if (!this.organizationId() || this.allSpaces().length === 0) {
      return null;
    }
    return {
      placeholder: this.translateService.instant('spaces.searchPlaceholder'),
      model: this.spaceService.searchQuery,
      leftIcon: 'search',
      class: 'page-header_search-input',
    };
  });

  readonly filtersConfig = computed<PageHeaderFilter[] | null>(() => {
    if (!this.organizationId() || this.allSpaces().length === 0) {
      return null;
    }
    return [
      {
        type: 'select',
        options: this.statusFilterOptions(),
        model: this.statusFilter,
        class: 'page-header_filter',
      },
    ];
  });

  handleCreateSpace(): void {
    const orgId = this.organizationId();
    if (!orgId) {
      return;
    }
    this.modal.open(CreateSpaceModal, this.viewContainerRef, {
      size: 'md',
      data: { organizationId: orgId },
    });
  }

  handleSpaceSettings(space: Space): void {
    const orgId = this.organizationId();
    if (orgId) {
      this.navigationService.navigateToSpaceSettings(orgId, space.id);
    }
  }

  handleRetry(): void {
    this.spaceService.spaces.reload();
  }

  handleGoToOrganizations(): void {
    this.navigationService.navigateToOrganizations();
  }

  goToPage(page: number): void {
    this.currentPage.set(page);
  }
}
