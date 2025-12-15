import { Component, ChangeDetectionStrategy, computed, inject, input } from '@angular/core';
import { LoadingState, ErrorState, EmptyState } from 'shared-ui';
import { PageService, Page } from '../../application/services/page.service';
import { NavigationService } from '../../application/services/navigation.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-page-list',
  imports: [LoadingState, ErrorState, EmptyState, TranslatePipe],
  template: `
    <div class="page-list">
      @if (pageService.isFetchingPages()) {
        <lib-loading-state [message]="'pages.loadingPages' | translate" />
      } @else if (pageService.hasPagesError()) {
        <lib-error-state
          [title]="'pages.failedToLoad' | translate"
          [message]="errorMessage()"
          [retryLabel]="'common.retry' | translate"
          (onRetry)="handleRetry()"
        />
      } @else if (pages().length === 0) {
        <lib-empty-state
          [title]="'pages.noPagesYet' | translate"
          [message]="'pages.noPagesYetDescription' | translate"
          icon="file-text"
        />
      } @else {
        <div class="page-list_items">
          @for (page of pages(); track page.id) {
            <div class="page-list_item" (click)="handlePageClick(page)">
              <div class="page-list_item-content">
                <h3 class="page-list_item-title">{{ page.title }}</h3>
                @if (page.commentCount !== undefined && page.commentCount > 0) {
                  <span class="page-list_item-meta">
                    {{ page.commentCount }} {{ getCommentLabel(page.commentCount) }}
                  </span>
                }
                <p class="page-list_item-date">
                  {{ 'pages.updated' | translate }} {{ formatDate(page.updatedAt) }}
                </p>
              </div>
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .page-list {
        @apply w-full;
      }

      .page-list_items {
        @apply flex flex-col;
        @apply gap-2;
      }

      .page-list_item {
        @apply p-4;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-bg-tertiary;
      }

      .page-list_item-content {
        @apply flex flex-col;
        @apply gap-2;
      }

      .page-list_item-title {
        @apply text-base font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .page-list_item-meta {
        @apply text-sm;
        @apply text-text-secondary;
      }

      .page-list_item-date {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageList {
  readonly pageService = inject(PageService);
  readonly navigationService = inject(NavigationService);
  private readonly translateService = inject(TranslateService);

  readonly spaceId = input.required<string>();

  readonly pages = computed(() => {
    const id = this.spaceId();
    if (!id) return [];
    return this.pageService.getRootPages(id);
  });

  readonly errorMessage = computed(() => {
    const error = this.pageService.error();
    if (error) {
      return error instanceof Error
        ? error.message
        : this.translateService.instant('pages.loadError');
    }
    return this.translateService.instant('common.unknownError');
  });

  getCommentLabel(count: number): string {
    return count === 1
      ? this.translateService.instant('comments.comment')
      : this.translateService.instant('comments.comments');
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }

  handlePageClick(page: Page): void {
    const organizationId = this.navigationService.currentOrganizationId();
    const spaceId = this.spaceId();

    if (organizationId && spaceId && page.id) {
      this.navigationService.navigateToPage(organizationId, spaceId, page.id);
    }
  }

  handleRetry(): void {
    this.pageService.reloadPages();
  }
}
