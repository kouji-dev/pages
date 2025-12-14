import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  ViewContainerRef,
} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LoadingState, ErrorState, Modal, Button } from 'shared-ui';
import { SpaceService } from '../../application/services/space.service';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { BackToPage } from '../components/back-to-page';
import { PageList } from '../components/page-list';
import { PagesTree } from '../components/pages-tree';
import { CreatePageModal } from '../components/create-page-modal';

@Component({
  selector: 'app-space-detail-page',
  imports: [RouterOutlet, LoadingState, ErrorState, BackToPage, PageList, PagesTree, Button],
  template: `
    <div class="space-detail-page">
      @if (spaceService.isFetchingSpace()) {
        <lib-loading-state message="Loading space..." />
      } @else if (spaceService.hasSpaceError()) {
        <lib-error-state
          title="Failed to Load Space"
          [message]="errorMessage()"
          [retryLabel]="'Retry'"
          (onRetry)="handleRetry()"
        />
      } @else if (!space()) {
        <lib-error-state
          title="Space Not Found"
          message="The space you're looking for doesn't exist or you don't have access to it."
          [showRetry]="false"
        />
      } @else {
        <div class="space-detail-page_header">
          <div class="space-detail-page_header-content">
            <app-back-to-page label="Back to Spaces" (onClick)="handleBackToSpaces()" />
            <div class="space-detail-page_header-main">
              <div class="space-detail-page_header-info">
                <div class="space-detail-page_key">{{ space()?.key }}</div>
                <h1 class="space-detail-page_title">{{ space()?.name }}</h1>
                @if (space()?.description) {
                  <p class="space-detail-page_description">{{ space()?.description }}</p>
                }
              </div>
              <div class="space-detail-page_header-actions">
                <lib-button
                  variant="primary"
                  size="sm"
                  (clicked)="handleCreatePage()"
                  leftIcon="plus"
                >
                  Create Page
                </lib-button>
              </div>
            </div>
          </div>
        </div>

        <div class="space-detail-page_content">
          <div class="space-detail-page_container">
            <div class="space-detail-page_sidebar">
              <app-pages-tree [spaceId]="spaceId()" />
            </div>
            <div class="space-detail-page_main">
              @if (showDefaultContent()) {
                <!-- Default content when no page is selected -->
                <div class="space-detail-page_default-content">
                  <div class="space-detail-page_section">
                    <h2 class="space-detail-page_section-title">Pages</h2>
                    <app-page-list [spaceId]="spaceId()" />
                  </div>

                  @if (space()?.recentPages && space()!.recentPages!.length > 0) {
                    <div class="space-detail-page_section">
                      <h2 class="space-detail-page_section-title">Recent Pages</h2>
                      <div class="space-detail-page_recent-pages">
                        @for (page of space()!.recentPages; track page.id) {
                          <div
                            class="space-detail-page_recent-page"
                            (click)="handlePageClick(page)"
                          >
                            <h3 class="space-detail-page_recent-page-title">{{ page.title }}</h3>
                            <p class="space-detail-page_recent-page-meta">
                              Updated {{ formatDate(page.updatedAt) }}
                            </p>
                          </div>
                        }
                      </div>
                    </div>
                  }
                </div>
              } @else {
                <!-- Page detail content when a page is selected -->
                <router-outlet />
              }
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .space-detail-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .space-detail-page_header {
        @apply w-full;
        @apply py-6;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .space-detail-page_header-content {
        @apply w-full;
      }

      .space-detail-page_header-main {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .space-detail-page_header-info {
        @apply flex items-center;
        @apply gap-4;
        @apply flex-wrap;
        @apply flex-1;
        @apply min-w-0;
      }

      .space-detail-page_header-actions {
        @apply flex items-center;
        @apply gap-2;
        @apply flex-shrink-0;
      }

      .space-detail-page_key {
        @apply text-xs font-mono font-semibold;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-bg-secondary;
        @apply text-text-secondary;
        @apply inline-block;
        @apply w-fit;
        @apply flex-shrink-0;
      }

      .space-detail-page_title {
        @apply text-2xl font-bold;
        @apply text-text-primary;
        margin: 0;
        @apply flex-shrink-0;
      }

      .space-detail-page_description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
        @apply flex-shrink-0;
      }

      .space-detail-page_content {
        @apply flex-1;
        @apply w-full;
        @apply flex;
        @apply min-h-0;
      }

      .space-detail-page_container {
        @apply w-full;
        @apply flex;
        @apply flex-1;
        @apply min-h-0;
      }

      .space-detail-page_sidebar {
        width: 256px; /* Fixed width: same as project sidebar */
        @apply flex-shrink-0;
        @apply border-r;
        @apply border-border-default;
        @apply flex flex-col;
        @apply h-full;
        @apply min-h-0;
        @apply bg-bg-secondary;
      }

      .space-detail-page_main {
        @apply flex-1;
        @apply min-w-0;
        @apply overflow-auto;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .space-detail-page_section {
        @apply flex flex-col;
        @apply gap-4;
      }

      .space-detail-page_section-title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .space-detail-page_placeholder {
        @apply text-base;
        @apply text-text-secondary;
        @apply text-center;
        @apply py-12;
        margin: 0;
      }

      .space-detail-page_recent-pages {
        @apply flex flex-col;
        @apply gap-4;
      }

      .space-detail-page_recent-page {
        @apply p-4;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-bg-tertiary;
      }

      .space-detail-page_recent-page-title {
        @apply text-base font-medium;
        @apply text-text-primary;
        margin: 0 0 0.5rem 0;
      }

      .space-detail-page_recent-page-meta {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SpaceDetailPage {
  readonly spaceService = inject(SpaceService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly spaceId = computed(() => {
    return this.navigationService.currentSpaceId() || '';
  });
  readonly space = computed(() => this.spaceService.currentSpace());

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  readonly pageId = computed(() => {
    return this.navigationService.currentPageId();
  });

  readonly showDefaultContent = computed(() => {
    return !this.pageId();
  });

  readonly errorMessage = computed(() => {
    const error = this.spaceService.spaceError();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading the space.';
    }
    return 'An unknown error occurred.';
  });

  handleRetry(): void {
    const id = this.spaceId();
    if (id) {
      this.spaceService.fetchSpace(id);
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }

  handleBackToSpaces(): void {
    const orgId = this.organizationId();
    if (orgId) {
      this.navigationService.navigateToOrganizationSpaces(orgId);
    }
  }

  handlePageClick(page: { id: string }): void {
    const orgId = this.organizationId();
    const spaceId = this.spaceId();

    if (orgId && spaceId && page.id) {
      this.navigationService.navigateToPage(orgId, spaceId, page.id);
    }
  }

  handleCreatePage(): void {
    const spaceId = this.spaceId();
    if (!spaceId) {
      return;
    }

    this.modal.open(CreatePageModal, this.viewContainerRef, {
      size: 'lg',
      data: { spaceId },
    });
  }
}
