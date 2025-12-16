import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  effect,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import {
  Button,
  Input,
  TextEditor,
  LoadingState,
  ErrorState,
  ToastService,
  Dropdown,
  Modal,
} from 'shared-ui';
import { PageService, Page } from '../../../../application/services/page.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { CommentList } from '../../../projects/components/comment-list/comment-list';

@Component({
  selector: 'app-page-detail-page',
  imports: [
    Button,
    Input,
    TextEditor,
    LoadingState,
    ErrorState,
    FormsModule,
    Dropdown,
    CommentList,
    TranslatePipe,
  ],
  template: `
    <div class="page-detail-page">
      @if (pageService.isFetchingPage()) {
        <lib-loading-state [message]="'pages.loadingPage' | translate" />
      } @else if (pageService.hasPageError()) {
        <lib-error-state
          [title]="'pages.failedToLoad' | translate"
          [message]="errorMessage()"
          [retryLabel]="'common.retry' | translate"
          (onRetry)="handleRetry()"
        />
      } @else if (!page()) {
        <lib-error-state
          [title]="'pages.notFound' | translate"
          [message]="'pages.notFoundDescription' | translate"
          [showRetry]="false"
        />
      } @else {
        <div class="page-detail-page_content">
          <div class="page-detail-page_header">
            <div class="page-detail-page_header-main">
              <lib-input
                [(model)]="title"
                [placeholder]="'pages.pageTitle' | translate"
                [required]="true"
                [readonly]="!isEditMode()"
                [errorMessage]="isEditMode() ? titleError() : ''"
                class="page-detail-page_title-input"
              />
              <div class="page-detail-page_header-actions">
                @if (isEditMode()) {
                  <lib-button
                    variant="secondary"
                    size="sm"
                    (clicked)="handleCancel()"
                    [disabled]="isSaving()"
                  >
                    {{ 'common.cancel' | translate }}
                  </lib-button>
                  <lib-button
                    variant="primary"
                    size="sm"
                    (clicked)="handleSave()"
                    [loading]="isSaving()"
                    [disabled]="!isFormValid()"
                  >
                    {{ 'common.save' | translate }}
                  </lib-button>
                } @else {
                  <lib-button variant="ghost" size="sm" (clicked)="handleEdit()" leftIcon="pencil">
                    {{ 'common.edit' | translate }}
                  </lib-button>
                  <lib-button
                    variant="ghost"
                    size="sm"
                    [iconOnly]="true"
                    leftIcon="ellipsis-vertical"
                    [libDropdown]="actionsDropdownTemplate"
                    [position]="'below'"
                    #actionsDropdown="libDropdown"
                  >
                  </lib-button>
                  <ng-template #actionsDropdownTemplate>
                    <lib-button
                      variant="ghost"
                      size="md"
                      leftIcon="trash"
                      [fullWidth]="true"
                      class="page-detail-page_delete-button"
                      (clicked)="handleDelete(actionsDropdown)"
                    >
                      {{ 'pages.deletePage' | translate }}
                    </lib-button>
                  </ng-template>
                }
              </div>
            </div>
            @if (!isEditMode()) {
              <div class="page-detail-page_metadata">
                @if (page()?.authorName) {
                  <span class="page-detail-page_metadata-item">
                    {{ 'pages.createdBy' | translate }} {{ page()!.authorName }}
                    @if (page()!.createdAt) {
                      {{ 'pages.on' | translate }} {{ formatDate(page()!.createdAt) }}
                    }
                  </span>
                }
                @if (page()?.editorName && page()?.editorName !== page()?.authorName) {
                  <span class="page-detail-page_metadata-item">
                    {{ 'pages.lastEditedBy' | translate }} {{ page()!.editorName }}
                    @if (page()!.updatedAt) {
                      {{ 'pages.on' | translate }} {{ formatDate(page()!.updatedAt) }}
                    }
                  </span>
                } @else if (page()?.updatedAt) {
                  <span class="page-detail-page_metadata-item">
                    {{ 'pages.lastUpdated' | translate }} {{ formatDate(page()!.updatedAt) }}
                  </span>
                }
              </div>
            }
          </div>

          <div class="page-detail-page_body">
            @if (isEditMode()) {
              <lib-text-editor
                #contentEditor
                [placeholder]="'pages.startWriting' | translate"
                [showToolbar]="true"
                [(ngModel)]="content"
                name="page-content"
                [initialValue]="initialContent()"
                (htmlChange)="contentHtml.set($event)"
                class="page-detail-page_editor"
              />
            } @else {
              <div class="page-detail-page_view-content">
                @if (page()?.content) {
                  <lib-text-editor
                    [readOnly]="true"
                    [showToolbar]="false"
                    [initialValue]="page()!.content!"
                    class="page-detail-page_view-editor"
                  />
                } @else {
                  <p class="page-detail-page_empty">{{ 'pages.noContent' | translate }}</p>
                }
              </div>
            }
          </div>

          @if (!isEditMode()) {
            <div class="page-detail-page_comments">
              <app-comment-list [pageId]="pageId()" />
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .page-detail-page {
        @apply w-full;
        @apply h-full;
        @apply overflow-auto;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .page-detail-page_content {
        @apply max-w-4xl mx-auto;
        @apply flex flex-col;
        @apply gap-6;
      }

      .page-detail-page_header {
        @apply flex flex-col;
        @apply gap-4;
      }

      .page-detail-page_header-main {
        @apply flex items-start;
        @apply gap-4;
        @apply w-full;
      }

      .page-detail-page_metadata {
        @apply flex flex-col;
        @apply gap-1;
        @apply mt-2;
      }

      .page-detail-page_metadata-item {
        @apply text-sm;
        @apply text-muted-foreground;
      }

      .page-detail-page_delete-button ::ng-deep .button {
        @apply justify-start;
      }

      ::ng-deep .lib-dropdown-panel {
        @apply flex;
      }

      .page-detail-page_title-input {
        @apply flex-1;
      }

      .page-detail-page_title-input ::ng-deep .input--readonly {
        @apply border-none;
        @apply bg-transparent;
        @apply shadow-none;
        @apply p-0;
      }

      .page-detail-page_title-input ::ng-deep .input--readonly .input-field {
        @apply text-3xl font-bold;
        @apply p-0;
        @apply cursor-text;
      }

      .page-detail-page_header-actions {
        @apply flex items-center;
        @apply gap-2;
        @apply flex-shrink-0;
      }

      .page-detail-page_title-input ::ng-deep .input--readonly {
        @apply border-none;
        @apply bg-transparent;
        @apply shadow-none;
        @apply p-0;
      }

      .page-detail-page_title-input ::ng-deep .input--readonly .input-field {
        @apply text-3xl font-bold;
        @apply p-0;
        @apply cursor-text;
      }

      .page-detail-page_body {
        @apply flex flex-col;
        @apply min-h-[400px];
      }

      .page-detail-page_editor {
        @apply w-full;
      }

      .page-detail-page_view-content {
        @apply w-full;
      }

      .page-detail-page_view-editor {
        @apply border-none;
      }

      .page-detail-page_view-editor ::ng-deep .text-editor {
        @apply border-none;
        @apply shadow-none;
      }

      .page-detail-page_view-editor ::ng-deep .text-editor_wrapper {
        @apply border-none;
      }

      .page-detail-page_view-editor ::ng-deep .text-editor_container {
        @apply min-h-0;
        @apply p-0;
        @apply border-none;
      }

      .page-detail-page_empty {
        @apply text-muted-foreground;
        @apply italic;
        @apply py-8;
        margin: 0;
      }

      .page-detail-page_comments {
        @apply mt-8;
        @apply pt-8;
        @apply border-t;
        @apply border-border;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageDetailPage {
  readonly pageService = inject(PageService);
  readonly navigationService = inject(NavigationService);
  private readonly translateService = inject(TranslateService);
  readonly toast = inject(ToastService);
  readonly modal = inject(Modal);

  @ViewChild('actionsDropdownTemplate') actionsDropdownTemplate!: TemplateRef<any>;

  readonly pageId = computed(() => {
    return this.navigationService.currentPageId() || '';
  });
  readonly page = computed(() => this.pageService.currentPage());

  readonly isEditMode = signal(false);
  readonly title = signal('');
  readonly content = signal('');
  readonly contentHtml = signal('');
  readonly initialContent = signal<string | undefined>(undefined);
  readonly isSaving = signal(false);

  // Initialize form when page loads
  private readonly initializeEffect = effect(
    () => {
      const page = this.page();
      if (page && !this.isEditMode()) {
        this.title.set(page.title);
        this.contentHtml.set(page.content || '');
        this.content.set(page.content || '');
        this.initialContent.set(page.content || undefined);
      }
    },
    { allowSignalWrites: true },
  );

  readonly errorMessage = computed(() => {
    const error = this.pageService.pageError();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading the page.';
    }
    return 'An unknown error occurred.';
  });

  readonly titleError = computed(() => {
    const titleValue = this.title();
    if (!titleValue || titleValue.trim() === '') {
      return this.translateService.instant('pages.titleRequired');
    }
    if (titleValue.length > 255) {
      return this.translateService.instant('pages.titleMaxLength');
    }
    return '';
  });

  readonly isFormValid = computed(() => {
    return !this.titleError() && this.title().trim() !== '';
  });

  readonly spaceId = computed(() => {
    return this.navigationService.currentSpaceId() || '';
  });

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  handleRetry(): void {
    const id = this.pageId();
    if (id) {
      this.pageService.fetchPage(id);
    }
  }

  handleBackToSpace(): void {
    const orgId = this.organizationId();
    const spaceId = this.spaceId();
    if (orgId && spaceId) {
      this.navigationService.navigateToSpace(orgId, spaceId);
    }
  }

  handleEdit(): void {
    this.isEditMode.set(true);
  }

  handleCancel(): void {
    const page = this.page();
    if (page) {
      this.title.set(page.title);
      this.contentHtml.set(page.content || '');
      this.content.set(page.content || '');
      this.initialContent.set(page.content || undefined);
    }
    this.isEditMode.set(false);
  }

  async handleSave(): Promise<void> {
    if (!this.isFormValid()) {
      return;
    }

    const pageId = this.pageId();
    if (!pageId) {
      return;
    }

    this.isSaving.set(true);

    try {
      await this.pageService.updatePage(pageId, {
        title: this.title(),
        content: this.contentHtml(),
      });

      this.toast.success('Page saved successfully');
      this.isEditMode.set(false);
    } catch (error) {
      console.error('Failed to save page:', error);
      this.toast.error('Failed to save page. Please try again.');
    } finally {
      this.isSaving.set(false);
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  async handleDelete(dropdown: Dropdown): Promise<void> {
    dropdown.open.set(false);

    const page = this.page();
    if (!page) {
      return;
    }

    if (
      !confirm(`Are you sure you want to delete "${page.title}"? This action cannot be undone.`)
    ) {
      return;
    }

    const pageId = this.pageId();
    if (!pageId) {
      return;
    }

    try {
      await this.pageService.deletePage(pageId);
      this.toast.success('Page deleted successfully');

      // Navigate back to space
      const orgId = this.organizationId();
      const spaceId = this.spaceId();
      if (orgId && spaceId) {
        this.navigationService.navigateToSpace(orgId, spaceId);
      }
    } catch (error) {
      console.error('Failed to delete page:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to delete page. Please try again.';
      this.toast.error(errorMessage);
    }
  }
}
