import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  input,
  signal,
  ViewChild,
  ViewContainerRef,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button, TextEditor, ToastService } from 'shared-ui';
import { CommentService } from '../../../../application/services/comment.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-comment-input',
  standalone: true,
  imports: [Button, TextEditor, FormsModule, TranslatePipe],
  template: `
    <div class="comment-input">
      <lib-text-editor
        #editor
        [placeholder]="'comments.addComment' | translate"
        [showToolbar]="true"
        [(ngModel)]="content"
        name="comment"
        (htmlChange)="htmlContent.set($event)"
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
          {{ 'comments.comment' | translate }}
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
  readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  readonly issueId = input<string>();
  readonly pageId = input<string>();

  @ViewChild('editor') editor?: TextEditor;

  readonly content = signal('');
  readonly htmlContent = signal('');
  readonly isSubmitting = signal(false);

  readonly contentError = computed(() => {
    const html = this.htmlContent();
    if (!html || html.trim() === '' || html.trim() === '<p></p>') {
      return '';
    }
    // Check text length (strip HTML tags for length check)
    const textContent = this.content();
    if (textContent.trim().length > 10000) {
      return this.translateService.instant('comments.maxLength');
    }
    return '';
  });

  readonly isValid = computed(() => {
    const html = this.htmlContent();
    const textContent = this.content();
    const issueId = this.issueId();
    const pageId = this.pageId();

    return (
      (issueId || pageId) &&
      html &&
      html.trim() !== '' &&
      html.trim() !== '<p></p>' &&
      textContent.trim().length > 0 &&
      !this.contentError()
    );
  });

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      // Use HTML content for rich text comments
      const html = this.htmlContent();
      const issueId = this.issueId();
      const pageId = this.pageId();

      if (issueId) {
        await this.commentService.createComment(issueId, {
          content: html,
        });
      } else if (pageId) {
        await this.commentService.createPageComment(pageId, {
          content: html,
        });
      } else {
        throw new Error('Either issueId or pageId must be provided');
      }

      this.toast.success(this.translateService.instant('comments.addSuccess'));
      this.content.set('');
      this.htmlContent.set('');
      // Clear the editor
      if (this.editor) {
        this.editor.setHtml('');
      }
    } catch (error) {
      console.error('Failed to create comment:', error);
      const errorMessage =
        error instanceof Error ? error.message : this.translateService.instant('comments.addError');
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
