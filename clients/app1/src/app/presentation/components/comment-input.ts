import { Component, ChangeDetectionStrategy, computed, inject, input, signal } from '@angular/core';
import { Button, Input } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { CommentService } from '../../application/services/comment.service';

@Component({
  selector: 'app-comment-input',
  standalone: true,
  imports: [Button, Input],
  template: `
    <div class="comment-input">
      <lib-input
        type="textarea"
        placeholder="Add a comment..."
        [(model)]="content"
        [rows]="3"
        [errorMessage]="contentError()"
      />
      <div class="comment-input_actions">
        <lib-button
          variant="primary"
          size="md"
          (clicked)="handleSubmit()"
          [loading]="isSubmitting()"
          [disabled]="!isValid()"
        >
          Comment
        </lib-button>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .comment-input {
        @apply flex flex-col;
        @apply gap-3;
      }

      .comment-input_actions {
        @apply flex items-center justify-end;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommentInput {
  private readonly commentService = inject(CommentService);
  private readonly toast = inject(ToastService);

  readonly issueId = input.required<string>();

  readonly content = signal('');
  readonly isSubmitting = signal(false);

  readonly contentError = computed(() => {
    const value = this.content();
    if (!value.trim()) {
      return '';
    }
    if (value.trim().length > 10000) {
      return 'Comment must be 10,000 characters or less';
    }
    return '';
  });

  readonly isValid = computed(() => {
    return !this.contentError() && this.content().trim().length > 0;
  });

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      await this.commentService.createComment(this.issueId(), {
        content: this.content().trim(),
      });

      this.toast.success('Comment added successfully!');
      this.content.set('');
    } catch (error) {
      console.error('Failed to create comment:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to add comment. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
