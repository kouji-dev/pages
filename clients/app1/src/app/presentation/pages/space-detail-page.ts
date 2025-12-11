import { Component, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { Button, LoadingState, ErrorState } from 'shared-ui';
import { SpaceService } from '../../application/services/space.service';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { BackToPage } from '../components/back-to-page';

@Component({
  selector: 'app-space-detail-page',
  imports: [Button, LoadingState, ErrorState, BackToPage],
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
            <div class="space-detail-page_header-main">
              <div class="space-detail-page_header-info">
                <app-back-to-page label="Back to Spaces" (onClick)="handleBackToSpaces()" />
                <div class="space-detail-page_key">{{ space()?.key }}</div>
                <h1 class="space-detail-page_title">{{ space()?.name }}</h1>
                @if (space()?.description) {
                  <p class="space-detail-page_description">{{ space()?.description }}</p>
                }
              </div>
            </div>
          </div>
        </div>

        <div class="space-detail-page_content">
          <div class="space-detail-page_container">
            <div class="space-detail-page_main">
              <div class="space-detail-page_section">
                <h2 class="space-detail-page_section-title">Pages</h2>
                <p class="space-detail-page_placeholder">
                  Page management will be available in Phase 1.4.6
                </p>
              </div>

              @if (space()?.recentPages && space()!.recentPages!.length > 0) {
                <div class="space-detail-page_section">
                  <h2 class="space-detail-page_section-title">Recent Pages</h2>
                  <div class="space-detail-page_recent-pages">
                    @for (page of space()!.recentPages; track page.id) {
                      <div class="space-detail-page_recent-page">
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
            <div class="space-detail-page_sidebar">
              <div class="space-detail-page_metadata">
                <h3 class="space-detail-page_metadata-title">Details</h3>
                <div class="space-detail-page_metadata-item">
                  <span class="space-detail-page_metadata-label">Pages</span>
                  <span class="space-detail-page_metadata-value">{{
                    space()!.pageCount || 0
                  }}</span>
                </div>
                <div class="space-detail-page_metadata-item">
                  <span class="space-detail-page_metadata-label">Created</span>
                  <span class="space-detail-page_metadata-value">{{
                    formatDate(space()!.createdAt!)
                  }}</span>
                </div>
                @if (space()?.updatedAt) {
                  <div class="space-detail-page_metadata-item">
                    <span class="space-detail-page_metadata-label">Updated</span>
                    <span class="space-detail-page_metadata-value">{{
                      formatDate(space()!.updatedAt!)
                    }}</span>
                  </div>
                }
              </div>
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
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .space-detail-page_header-content {
        @apply max-w-7xl mx-auto;
      }

      .space-detail-page_header-main {
        @apply flex items-start justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .space-detail-page_header-info {
        @apply flex flex-col;
        @apply gap-2;
      }

      .space-detail-page_key {
        @apply text-xs font-mono font-semibold;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-bg-secondary;
        @apply text-text-secondary;
        @apply inline-block;
        @apply w-fit;
      }

      .space-detail-page_title {
        @apply text-3xl font-bold;
        @apply text-text-primary;
        margin: 0;
      }

      .space-detail-page_description {
        @apply text-base;
        @apply text-text-secondary;
        margin: 0;
      }

      .space-detail-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .space-detail-page_container {
        @apply max-w-7xl mx-auto;
        @apply grid grid-cols-1 lg:grid-cols-3;
        @apply gap-8;
      }

      .space-detail-page_main {
        @apply lg:col-span-2;
        @apply flex flex-col;
        @apply gap-6;
      }

      .space-detail-page_sidebar {
        @apply lg:col-span-1;
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

      .space-detail-page_metadata {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-6;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .space-detail-page_metadata-title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0 0 1rem 0;
      }

      .space-detail-page_metadata-item {
        @apply flex flex-col;
        @apply gap-2;
      }

      .space-detail-page_metadata-label {
        @apply text-sm font-medium;
        @apply text-text-secondary;
      }

      .space-detail-page_metadata-value {
        @apply text-sm;
        @apply text-text-primary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SpaceDetailPage {
  readonly spaceService = inject(SpaceService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);

  readonly spaceId = computed(() => {
    return this.navigationService.currentSpaceId() || '';
  });
  readonly space = computed(() => this.spaceService.currentSpace());

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
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
}
