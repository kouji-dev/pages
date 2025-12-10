import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  effect,
  ViewChild,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input, TextEditor } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { IssueService, UpdateIssueRequest, Issue } from '../../application/services/issue.service';

type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';
type IssuePriority = 'low' | 'medium' | 'high' | 'critical';

@Component({
  selector: 'app-edit-issue-modal',
  imports: [
    ModalContainer,
    ModalHeader,
    ModalContent,
    ModalFooter,
    Button,
    Input,
    TextEditor,
    FormsModule,
  ],
  template: `
    <lib-modal-container>
      <lib-modal-header>Edit Issue</lib-modal-header>
      <lib-modal-content>
        <form class="edit-issue-form" (ngSubmit)="handleSubmit()">
          <lib-input
            label="Title"
            placeholder="Enter issue title"
            [(model)]="title"
            [required]="true"
            [errorMessage]="titleError()"
          />
          <div class="edit-issue-form_field">
            <label class="edit-issue-form_label">Description</label>
            <lib-text-editor
              #descriptionEditor
              placeholder="Describe the issue in detail"
              [(ngModel)]="description"
              name="description"
              (htmlChange)="descriptionHtml.set($event)"
              [showToolbar]="true"
            />
          </div>
          <div class="edit-issue-form_row">
            <div class="edit-issue-form_field">
              <label class="edit-issue-form_label">Status</label>
              <select
                class="edit-issue-form_select"
                [value]="status()"
                (change)="status.set($any($event.target).value)"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div class="edit-issue-form_field">
              <label class="edit-issue-form_label">Priority</label>
              <select
                class="edit-issue-form_select"
                [value]="priority()"
                (change)="priority.set($any($event.target).value)"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>
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

      .edit-issue-form {
        @apply flex flex-col gap-4;
      }

      .edit-issue-form_row {
        @apply grid grid-cols-2 gap-4;
      }

      .edit-issue-form_field {
        @apply flex flex-col gap-2;
      }

      .edit-issue-form_label {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .edit-issue-form_select {
        @apply px-3 py-2;
        @apply border border-border-default;
        @apply rounded-md;
        @apply bg-bg-primary;
        @apply text-text-primary;
        @apply focus:outline-none focus:ring-2 focus:ring-primary-500;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditIssueModal {
  private readonly issueService = inject(IssueService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);

  readonly issueId = input.required<string>();
  readonly issue = input.required<Issue>();

  readonly title = signal('');
  readonly description = signal('');
  readonly descriptionHtml = signal('');
  readonly status = signal<IssueStatus>('todo');
  readonly priority = signal<IssuePriority>('medium');
  readonly isSubmitting = signal(false);

  @ViewChild('descriptionEditor') descriptionEditor?: TextEditor;

  private readonly initializeEffect = effect(
    () => {
      const issue = this.issue();
      if (issue) {
        this.title.set(issue.title);
        const desc = issue.description || '';
        this.description.set(desc);
        this.descriptionHtml.set(desc);
        this.status.set(issue.status);
        this.priority.set(issue.priority);
        // Set HTML in editor if it's HTML content
        if (this.descriptionEditor && desc) {
          this.descriptionEditor.setHtml(desc);
        }
      }
    },
    { allowSignalWrites: true },
  );

  readonly titleError = computed(() => {
    const value = this.title();
    if (!value.trim()) {
      return 'Title is required';
    }
    if (value.trim().length > 255) {
      return 'Title must be 255 characters or less';
    }
    return '';
  });

  readonly isValid = computed(() => {
    return !this.titleError() && this.title().trim().length > 0;
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
      const request: UpdateIssueRequest = {
        title: this.title().trim(),
        description: this.descriptionHtml().trim() || undefined,
        status: this.status(),
        priority: this.priority(),
      };

      await this.issueService.updateIssue(this.issueId(), request);

      this.toast.success('Issue updated successfully!');
      this.modal.close();
    } catch (error) {
      console.error('Failed to update issue:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update issue. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
