import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  effect,
} from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input } from 'shared-ui';
import { ToastService } from 'shared-ui';
import {
  CommentService,
  Comment,
  UpdateCommentRequest,
} from '../../application/services/comment.service';

@Component({
  selector: 'app-edit-comment-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input],
  template: `
    <lib-modal-container>
      <lib-modal-header>Edit Comment</lib-modal-header>
      <lib-modal-content>
        <form class="edit-comment-form" (ngSubmit)="handleSubmit()">
          <lib-input
            type="textarea"
            placeholder="Enter your comment"
            [(model)]="content"
            [rows]="4"
            [errorMessage]="contentError()"
          />
        </form>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isSubmitting()">
          Cancel
        </lib-button>
        <lib-button
          variant="primary"
          (clicked)="handleSubmit()"
          [loading]="isSubmitting()"
          [disabled]="!isValid()"
        >
          Save Changes
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .edit-comment-form {
        @apply flex flex-col gap-4;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditCommentModal {
  private readonly commentService = inject(CommentService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);

  readonly commentId = input.required<string>();
  readonly comment = input.required<Comment>();

  readonly content = signal('');
  readonly isSubmitting = signal(false);

  private readonly initializeEffect = effect(
    () => {
      const comment = this.comment();
      if (comment) {
        this.content.set(comment.content);
      }
    },
    { allowSignalWrites: true },
  );

  readonly contentError = computed(() => {
    const value = this.content();
    if (!value.trim()) {
      return 'Comment content is required';
    }
    if (value.trim().length > 10000) {
      return 'Comment must be 10,000 characters or less';
    }
    return '';
  });

  readonly isValid = computed(() => {
    return !this.contentError() && this.content().trim().length > 0;
  });

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      const request: UpdateCommentRequest = {
        content: this.content().trim(),
      };

      await this.commentService.updateComment(this.commentId(), request);

      this.toast.success('Comment updated successfully!');
      this.modal.close();
    } catch (error) {
      console.error('Failed to update comment:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update comment. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
