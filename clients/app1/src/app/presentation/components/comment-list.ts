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
import { CommentService, Comment } from '../../application/services/comment.service';
import { CommentInput } from './comment-input';
import { EditCommentModal } from './edit-comment-modal';

@Component({
  selector: 'app-comment-list',
  standalone: true,
  imports: [Button, CommentInput, TextEditor],
  template: `
    <div class="comment-list">
      <div class="comment-list_header">
        <h3 class="comment-list_title">Comments</h3>
      </div>

      <app-comment-input [issueId]="issueId()" />

      <div class="comment-list_items">
        @if (commentService.isLoading()) {
          <div class="comment-list_loading">Loading comments...</div>
        } @else if (comments().length === 0) {
          <div class="comment-list_empty">No comments yet. Be the first to comment!</div>
        } @else {
          @for (comment of comments(); track comment.id) {
            <div class="comment-list_item">
              <div class="comment-list_item-header">
                <div class="comment-list_item-author">
                  <span class="comment-list_item-author-name">{{ comment.user_name }}</span>
                  <span class="comment-list_item-date">{{ formatDate(comment.created_at) }}</span>
                  @if (comment.is_edited) {
                    <span class="comment-list_item-edited">(edited)</span>
                  }
                </div>
                <div class="comment-list_item-actions">
                  <lib-button variant="ghost" size="sm" (clicked)="handleEditComment(comment)">
                    Edit
                  </lib-button>
                  <lib-button variant="ghost" size="sm" (clicked)="handleDeleteComment(comment)">
                    Delete
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
        @apply text-text-primary;
        margin: 0;
      }

      .comment-list_items {
        @apply flex flex-col;
        @apply gap-4;
      }

      .comment-list_loading,
      .comment-list_empty {
        @apply text-sm;
        @apply text-text-secondary;
        @apply text-center;
        @apply py-8;
      }

      .comment-list_item {
        @apply flex flex-col;
        @apply gap-2;
        @apply p-4;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .comment-list_item-header {
        @apply flex items-center justify-between;
      }

      .comment-list_item-author {
        @apply flex items-center gap-2;
      }

      .comment-list_item-author-name {
        @apply font-semibold;
        @apply text-text-primary;
      }

      .comment-list_item-date {
        @apply text-xs;
        @apply text-text-secondary;
      }

      .comment-list_item-edited {
        @apply text-xs;
        @apply text-text-secondary;
        @apply italic;
      }

      .comment-list_item-actions {
        @apply flex items-center gap-2;
      }

      .comment-list_item-content {
        @apply text-sm;
        @apply text-text-primary;
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

  readonly issueId = input.required<string>();

  readonly comments = computed(() => this.commentService.commentsList());

  private readonly initializeEffect = effect(
    () => {
      const issueId = this.issueId();
      if (issueId) {
        this.commentService.setIssue(issueId);
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
    if (!confirm('Are you sure you want to delete this comment?')) {
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
