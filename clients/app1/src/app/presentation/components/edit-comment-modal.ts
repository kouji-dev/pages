import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  effect,
  ViewChild,
  ViewContainerRef,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, TextEditor, ToastService } from 'shared-ui';
import {
  CommentService,
  Comment,
  UpdateCommentRequest,
} from '../../application/services/comment.service';

@Component({
  selector: 'app-edit-comment-modal',
  imports: [
    ModalContainer,
    ModalHeader,
    ModalContent,
    ModalFooter,
    Button,
    TextEditor,
    FormsModule,
  ],
  template: `
    <lib-modal-container>
      <lib-modal-header>Edit Comment</lib-modal-header>
      <lib-modal-content>
        <form class="edit-comment-form" (ngSubmit)="handleSubmit()">
          <lib-text-editor
            #editor
            placeholder="Enter your comment"
            [showToolbar]="true"
            [(ngModel)]="content"
            name="edit-comment"
            [initialValue]="initialHtml()"
            (htmlChange)="htmlContent.set($event)"
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
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly commentId = input.required<string>();
  readonly comment = input.required<Comment>();

  @ViewChild('editor') editor?: TextEditor;

  readonly content = signal('');
  readonly htmlContent = signal('');
  readonly initialHtml = signal<string | undefined>(undefined);
  readonly isSubmitting = signal(false);

  private readonly initializeEffect = effect(
    () => {
      const comment = this.comment();
      if (comment) {
        // Set initial HTML content for the editor
        this.initialHtml.set(comment.content);
        this.htmlContent.set(comment.content);
        // Also set text content for validation
        this.content.set(comment.content);
      }
    },
    { allowSignalWrites: true },
  );

  readonly contentError = computed(() => {
    const html = this.htmlContent();
    if (!html || html.trim() === '' || html.trim() === '<p></p>') {
      return 'Comment content is required';
    }
    // Check text length (strip HTML tags for length check)
    const textContent = this.content();
    if (textContent.trim().length > 10000) {
      return 'Comment must be 10,000 characters or less';
    }
    return '';
  });

  readonly isValid = computed(() => {
    const html = this.htmlContent();
    const textContent = this.content();
    return (
      html &&
      html.trim() !== '' &&
      html.trim() !== '<p></p>' &&
      textContent.trim().length > 0 &&
      !this.contentError()
    );
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
      // Use HTML content for rich text comments
      const html = this.htmlContent();
      const request: UpdateCommentRequest = {
        content: html,
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
