import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  input,
  signal,
  ViewContainerRef,
  effect,
} from '@angular/core';
import { Button, Modal, TextEditor } from 'shared-ui';
import { CommentService, Comment } from '../../../../application/services/comment.service';
import { CommentInput } from '../comment-input/comment-input';
import { EditCommentModal } from '../edit-comment-modal/edit-comment-modal';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-comment-list',
  standalone: true,
  imports: [Button, CommentInput, TextEditor, TranslatePipe],
  template: `
    <div class="comment-list">
      <div class="comment-list_header">
        <h3 class="comment-list_title">{{ 'comments.title' | translate }}</h3>
      </div>

      <app-comment-input [issueId]="issueId()" [pageId]="pageId()" />

      <div class="comment-list_items">
        @if (commentService.isLoading()) {
          <div class="comment-list_loading">{{ 'comments.loading' | translate }}</div>
        } @else if (comments().length === 0) {
          <div class="comment-list_empty">{{ 'comments.noComments' | translate }}</div>
        } @else {
          @for (comment of comments(); track comment.id) {
            <div class="comment-list_item">
              <div class="comment-list_item-header">
                <div class="comment-list_item-author">
                  <span class="comment-list_item-author-name">{{ comment.user_name }}</span>
                  <span class="comment-list_item-date">{{ formatDate(comment.created_at) }}</span>
                  @if (comment.is_edited) {
                    <span class="comment-list_item-edited"
                      >({{ 'comments.edited' | translate }})</span
                    >
                  }
                </div>
                <div class="comment-list_item-actions">
                  <lib-button variant="ghost" size="sm" (clicked)="handleEditComment(comment)">
                    {{ 'common.edit' | translate }}
                  </lib-button>
                  <lib-button variant="ghost" size="sm" (clicked)="handleDeleteComment(comment)">
                    {{ 'common.delete' | translate }}
                  </lib-button>
                </div>
              </div>
              <div class="comment-list_item-content">
                <lib-text-editor
                  [readOnly]="true"
                  [showToolbar]="false"
                  [initialValue]="comment.content"
                />
              </div>
            </div>
          }
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .comment-list {
        @apply flex flex-col;
        @apply gap-4;
      }

      .comment-list_header {
        @apply flex items-center justify-between;
      }

      .comment-list_title {
        @apply text-lg font-semibold;
        @apply text-foreground;
        margin: 0;
      }

      .comment-list_items {
        @apply flex flex-col;
        @apply gap-4;
      }

      .comment-list_loading,
      .comment-list_empty {
        @apply text-sm;
        @apply text-muted-foreground;
        @apply text-center;
        @apply py-8;
      }

      .comment-list_item {
        @apply flex flex-col;
        @apply gap-2;
        @apply p-4;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-muted;
      }

      .comment-list_item-header {
        @apply flex items-center justify-between;
      }

      .comment-list_item-author {
        @apply flex items-center gap-2;
      }

      .comment-list_item-author-name {
        @apply font-semibold;
        @apply text-foreground;
      }

      .comment-list_item-date {
        @apply text-xs;
        @apply text-muted-foreground;
      }

      .comment-list_item-edited {
        @apply text-xs;
        @apply text-muted-foreground;
        @apply italic;
      }

      .comment-list_item-actions {
        @apply flex items-center gap-2;
      }

      .comment-list_item-content {
        @apply text-sm;
        @apply text-foreground;
      }

      /* Style read-only text editor in comments to look like rendered content */
      :host ::ng-deep .comment-list_item-content .text-editor {
        @apply border-none;
        @apply bg-transparent;
      }

      :host ::ng-deep .comment-list_item-content .text-editor_wrapper {
        @apply min-h-0;
      }

      :host ::ng-deep .comment-list_item-content .text-editor_container {
        @apply min-h-0;
        @apply p-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommentList {
  readonly commentService = inject(CommentService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  readonly issueId = input<string>();
  readonly pageId = input<string>();

  readonly comments = computed(() => this.commentService.commentsList());

  private readonly initializeEffect = effect(
    () => {
      const issueId = this.issueId();
      const pageId = this.pageId();

      if (issueId) {
        this.commentService.setIssue(issueId);
        this.commentService.loadComments();
      } else if (pageId) {
        this.commentService.setPage(pageId);
        this.commentService.loadComments();
      }
    },
    { allowSignalWrites: true },
  );

  handleEditComment(comment: Comment): void {
    this.modal.open(EditCommentModal, this.viewContainerRef, {
      size: 'md',
      data: { commentId: comment.id, comment },
    });
  }

  async handleDeleteComment(comment: Comment): Promise<void> {
    if (!confirm(this.translateService.instant('comments.deleteConfirm'))) {
      return;
    }

    try {
      await this.commentService.deleteComment(comment.id);
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString();
  }
}
