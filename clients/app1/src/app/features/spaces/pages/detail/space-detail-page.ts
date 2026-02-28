import {
  Component,
  ChangeDetectionStrategy,
  computed,
  effect,
  inject,
  signal,
  ViewContainerRef,
} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LoadingState, ErrorState, Modal, Button, Badge, Avatar, Icon } from 'shared-ui';
import { SpaceService } from '../../../../application/services/space.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { BackToPage } from '../../../../shared/components/back-to-page/back-to-page.component';
import { PageList } from '../../../pages/components/page-list/page-list';
import { PagesTree } from '../../../pages/components/pages-tree/pages-tree';
import { CreatePageModal } from '../../../pages/components/create-page-modal/create-page-modal';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { PageContent } from '../../../../shared/layout/page-content/page-content';

@Component({
  selector: 'app-space-detail-page',
  imports: [
    RouterOutlet,
    LoadingState,
    ErrorState,
    BackToPage,
    PageList,
    PagesTree,
    Button,
    Badge,
    Avatar,
    Icon,
    TranslatePipe,
    PageContent,
  ],
  template: `
    @if (spaceService.isFetchingSpace()) {
      <lib-loading-state [message]="'spaces.loadingSpace' | translate" />
    } @else if (spaceService.hasSpaceError()) {
      <lib-error-state
        [title]="'spaces.failedToLoad' | translate"
        [message]="errorMessage()"
        [retryLabel]="'common.retry' | translate"
        (onRetry)="handleRetry()"
      />
    } @else if (!space()) {
      <lib-error-state
        [title]="'spaces.notFound' | translate"
        [message]="'spaces.notFoundDescription' | translate"
        [showRetry]="false"
      />
    } @else {
      <div class="space-detail-page_header">
        <div class="space-detail-page_header-content">
          <app-back-to-page
            [label]="'spaces.backToSpaces' | translate"
            (onClick)="handleBackToSpaces()"
          />
          <div class="space-detail-page_header-main">
            <div class="space-detail-page_header-info">
              <div class="space-detail-page_key">{{ space()?.key }}</div>
              <h1 class="space-detail-page_title">{{ space()?.name }}</h1>
              @if (space()?.description) {
                <p class="space-detail-page_description">{{ space()?.description }}</p>
              }
            </div>
            <div class="space-detail-page_header-actions">
              <lib-button variant="ghost" size="sm" (clicked)="toggleDetailsPanel()">
                {{
                  (isDetailsPanelOpen() ? 'spaces.hideDetailsPanel' : 'spaces.showDetailsPanel')
                    | translate
                }}
              </lib-button>
              <lib-button
                variant="primary"
                size="sm"
                (clicked)="handleCreatePage()"
                leftIcon="plus"
              >
                {{ 'pages.createPage' | translate }}
              </lib-button>
            </div>
          </div>
        </div>
      </div>

      <app-page-content [noPadding]="true">
        <div class="space-detail-page_container">
          <div class="space-detail-page_sidebar">
            <app-pages-tree [spaceId]="spaceId()" />
          </div>
          <div class="space-detail-page_main">
            <div class="space-detail-page_canvas">
              <div class="space-detail-page_display-content">
                @if (showDefaultContent()) {
                  <!-- Default content when no page is selected -->
                  <div class="space-detail-page_default-content">
                    <div class="space-detail-page_section">
                      <h2 class="space-detail-page_section-title">
                        {{ 'pages.title' | translate }}
                      </h2>
                      <app-page-list [spaceId]="spaceId()" />
                    </div>

                    @if (space()?.recentPages && space()!.recentPages!.length > 0) {
                      <div class="space-detail-page_section">
                        <h2 class="space-detail-page_section-title">
                          {{ 'pages.recentPages' | translate }}
                        </h2>
                        <div class="space-detail-page_recent-pages">
                          @for (page of space()!.recentPages; track page.id) {
                            <div
                              class="space-detail-page_recent-page"
                              (click)="handlePageClick(page)"
                            >
                              <h3 class="space-detail-page_recent-page-title">{{ page.title }}</h3>
                              <p class="space-detail-page_recent-page-meta">
                                {{ 'pages.updated' | translate }} {{ formatDate(page.updatedAt) }}
                              </p>
                            </div>
                          }
                        </div>
                      </div>
                    }
                  </div>
                } @else {
                  <!-- Page detail content when a page is selected -->
                  <div class="space-detail-page_page-route">
                    <router-outlet />
                  </div>
                }
              </div>
            </div>
          </div>
          @if (isDetailsPanelOpen()) {
            <div class="space-detail-page_details-rail">
              <div class="space-detail-page_details-header">
                <h3 class="space-detail-page_details-title-main">
                  {{ 'spaces.detailsPanel' | translate }}
                </h3>
                <lib-icon
                  name="external-link"
                  size="sm"
                  class="space-detail-page_details-header-icon"
                />
              </div>

              <div class="space-detail-page_details-section">
                <div class="space-detail-page_detail-item">
                  <span class="space-detail-page_detail-label">{{
                    'spaces.owner' | translate
                  }}</span>
                  <span class="space-detail-page_detail-value">
                    @if (space()?.owner) {
                      <span class="space-detail-page_detail-owner">
                        <lib-avatar
                          [avatarUrl]="space()?.owner?.avatar_url || undefined"
                          [name]="space()!.owner!.name"
                          [initials]="getInitials(space()!.owner!.name)"
                          size="xs"
                        />
                        {{ space()!.owner!.name }}
                      </span>
                    } @else {
                      {{ 'spaces.unassigned' | translate }}
                    }
                  </span>
                </div>
                <div class="space-detail-page_detail-item">
                  <span class="space-detail-page_detail-label">{{
                    'spaces.status' | translate
                  }}</span>
                  <span class="space-detail-page_detail-value">
                    <lib-badge [variant]="getStatusVariant()" size="sm">
                      {{ getStatusLabel() }}
                    </lib-badge>
                  </span>
                </div>
                <div class="space-detail-page_detail-item">
                  <span class="space-detail-page_detail-label">{{
                    'spaces.created' | translate
                  }}</span>
                  <span class="space-detail-page_detail-value">
                    {{ space()?.createdAt ? formatDate(space()?.createdAt ?? '') : '-' }}
                  </span>
                </div>
                <div class="space-detail-page_detail-item">
                  <span class="space-detail-page_detail-label">{{
                    'spaces.updated' | translate
                  }}</span>
                  <span class="space-detail-page_detail-value">
                    {{ space()?.updatedAt ? formatDate(space()?.updatedAt ?? '') : '-' }}
                  </span>
                </div>
              </div>

              <div class="space-detail-page_details-separator"></div>

              <div class="space-detail-page_details-section">
                <h3 class="space-detail-page_details-title">
                  {{ 'spaces.onThisPage' | translate }}
                </h3>
                @if (showDefaultContent()) {
                  <p class="space-detail-page_details-empty">
                    {{ 'spaces.selectPageForOutline' | translate }}
                  </p>
                } @else {
                  <nav class="space-detail-page_outline-list">
                    <a href="#overview" class="space-detail-page_outline-item">Overview</a>
                    <a href="#details" class="space-detail-page_outline-item">Details</a>
                    <a href="#notes" class="space-detail-page_outline-item">Notes</a>
                  </nav>
                }
              </div>

              <div class="space-detail-page_details-separator"></div>

              <div class="space-detail-page_details-section">
                <h3 class="space-detail-page_details-title">
                  {{ 'spaces.linkedIssues' | translate }}
                </h3>
                <p class="space-detail-page_details-empty">
                  {{ 'spaces.linkedIssuesUnavailable' | translate }}
                </p>
              </div>
            </div>
          }
        </div>
      </app-page-content>
    }
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        display: contents;
      }

      .space-detail-page_header {
        @apply w-full;
        @apply py-6;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border;
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
        @apply bg-muted;
        @apply text-muted-foreground;
        @apply inline-block;
        @apply w-fit;
        @apply flex-shrink-0;
      }

      .space-detail-page_title {
        @apply text-2xl font-bold;
        @apply text-foreground;
        margin: 0;
        @apply flex-shrink-0;
      }

      .space-detail-page_description {
        @apply text-sm;
        @apply text-muted-foreground;
        margin: 0;
        @apply flex-shrink-0;
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
        @apply border-border;
        @apply flex flex-col;
        @apply h-full;
        @apply min-h-0;
        @apply bg-muted;
      }

      .space-detail-page_main {
        @apply flex-1;
        @apply flex flex-col;
        @apply min-w-0;
        @apply min-h-0;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .space-detail-page_canvas {
        @apply w-full;
        @apply max-w-4xl;
        @apply mx-auto;
        @apply flex-1;
        @apply flex flex-col;
        @apply min-h-0;
      }

      .space-detail-page_display-content {
        @apply flex-1;
        @apply min-h-0;
        @apply flex flex-col;
        @apply overflow-hidden;
        @apply shadow-sm;
      }

      .space-detail-page_default-content {
        @apply flex-1;
        @apply min-h-0;
        @apply overflow-auto;
        @apply p-6;
      }

      .space-detail-page_page-route {
        @apply flex-1;
        @apply min-h-0;
        @apply flex flex-col;
        @apply overflow-hidden;
      }

      .space-detail-page_details-rail {
        width: 320px;
        @apply flex-shrink-0;
        @apply border-l border-border;
        @apply bg-card/50;
        @apply p-4;
        @apply overflow-auto;
      }

      .space-detail-page_details-header {
        @apply flex items-center justify-between;
        @apply mb-5;
      }

      .space-detail-page_details-title-main {
        @apply text-sm font-semibold uppercase tracking-wide text-muted-foreground;
        margin: 0;
      }

      .space-detail-page_details-header-icon {
        @apply text-muted-foreground;
      }

      .space-detail-page_details-section {
        @apply mb-6;
      }

      .space-detail-page_details-title {
        @apply text-sm font-semibold uppercase tracking-wide text-muted-foreground;
        @apply mb-3;
        margin: 0;
      }

      .space-detail-page_detail-item {
        @apply flex items-center justify-between gap-3;
        @apply py-1.5;
      }

      .space-detail-page_detail-label {
        @apply text-xs text-muted-foreground;
      }

      .space-detail-page_detail-value {
        @apply text-sm text-foreground;
        @apply inline-flex items-center;
      }

      .space-detail-page_detail-owner {
        @apply inline-flex items-center gap-2;
      }

      .space-detail-page_details-empty {
        @apply text-sm text-muted-foreground;
        margin: 0;
      }

      .space-detail-page_details-separator {
        @apply h-px bg-border;
        @apply my-5;
      }

      .space-detail-page_outline-list {
        @apply flex flex-col gap-1;
      }

      .space-detail-page_outline-item {
        @apply text-sm text-muted-foreground no-underline;
        @apply hover:text-foreground;
      }

      .space-detail-page_linked-issues {
        @apply flex flex-col gap-2;
      }

      .space-detail-page_linked-issue {
        @apply rounded-md border border-border bg-muted/30 p-2;
      }

      .space-detail-page_linked-issue-id {
        @apply text-xs font-mono text-muted-foreground;
        @apply mb-1;
      }

      .space-detail-page_linked-issue-title {
        @apply text-sm text-foreground;
        margin: 0;
      }

      .space-detail-page_section {
        @apply flex flex-col;
        @apply gap-4;
      }

      .space-detail-page_section-title {
        @apply text-lg font-semibold;
        @apply text-foreground;
        margin: 0;
      }

      .space-detail-page_placeholder {
        @apply text-base;
        @apply text-muted-foreground;
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
        @apply border-border;
        @apply bg-card;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-muted;
      }

      .space-detail-page_recent-page-title {
        @apply text-base font-medium;
        @apply text-foreground;
        margin: 0 0 0.5rem 0;
      }

      .space-detail-page_recent-page-meta {
        @apply text-sm;
        @apply text-muted-foreground;
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
  private readonly translateService = inject(TranslateService);

  readonly spaceId = computed(() => {
    return this.navigationService.currentSpaceId() || '';
  });
  readonly space = computed(() => this.spaceService.currentSpace());
  readonly isDetailsPanelOpen = signal<boolean>(true);

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
      return error instanceof Error
        ? error.message
        : this.translateService.instant('spaces.loadError');
    }
    return this.translateService.instant('common.unknownError');
  });

  constructor() {
    effect(() => {
      const pageId = this.pageId();
      const orgId = this.organizationId();
      const spaceId = this.spaceId();
      const space = this.space();

      if (pageId || !orgId || !spaceId || !space) {
        return;
      }

      const firstPageId = space.recentPages?.[0]?.id;
      if (!firstPageId) {
        return;
      }

      this.navigationService.navigateToPage(orgId, spaceId, firstPageId);
    });
  }

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

  toggleDetailsPanel(): void {
    this.isDetailsPanelOpen.update((open) => !open);
  }

  getStatusLabel(): string {
    const status = this.space()?.status;
    if (status === 'draft') return 'Draft';
    if (status === 'in-review') return 'In Review';
    if (status === 'published') return 'Published';
    return '-';
  }

  getStatusVariant(): 'default' | 'success' | 'warning' | 'danger' {
    const status = this.space()?.status;
    if (status === 'published') return 'success';
    if (status === 'in-review') return 'warning';
    if (status === 'draft') return 'default';
    return 'default';
  }

  getInitials(name: string): string {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }
}
