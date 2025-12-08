import { Component, ChangeDetectionStrategy, signal, computed, inject, input } from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { IssueService, CreateIssueRequest } from '../../application/services/issue.service';

type IssueType = 'task' | 'bug' | 'story' | 'epic';
type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';
type IssuePriority = 'low' | 'medium' | 'high' | 'critical';

@Component({
  selector: 'app-create-issue-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input],
  template: `
    <lib-modal-container>
      <lib-modal-header>Create Issue</lib-modal-header>
      <lib-modal-content>
        <form class="create-issue-form" (ngSubmit)="handleSubmit()">
          <lib-input
            label="Title"
            placeholder="Enter issue title"
            [(model)]="title"
            [required]="true"
            [errorMessage]="titleError()"
            helperText="Brief description of the issue"
          />
          <lib-input
            label="Description"
            type="textarea"
            placeholder="Describe the issue in detail (optional)"
            [(model)]="description"
            [rows]="4"
            helperText="Detailed description of the issue"
          />
          <div class="create-issue-form_row">
            <div class="create-issue-form_field">
              <label class="create-issue-form_label">Type</label>
              <select
                class="create-issue-form_select"
                [value]="type()"
                (change)="type.set($any($event.target).value)"
              >
                <option value="task">Task</option>
                <option value="bug">Bug</option>
                <option value="story">Story</option>
                <option value="epic">Epic</option>
              </select>
            </div>
            <div class="create-issue-form_field">
              <label class="create-issue-form_label">Priority</label>
              <select
                class="create-issue-form_select"
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
          Create Issue
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .create-issue-form {
        @apply flex flex-col gap-4;
      }

      .create-issue-form_row {
        @apply grid grid-cols-2 gap-4;
      }

      .create-issue-form_field {
        @apply flex flex-col gap-2;
      }

      .create-issue-form_label {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .create-issue-form_select {
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
export class CreateIssueModal {
  private readonly issueService = inject(IssueService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);

  readonly projectId = input.required<string>();

  readonly title = signal('');
  readonly description = signal('');
  readonly type = signal<IssueType>('task');
  readonly priority = signal<IssuePriority>('medium');
  readonly isSubmitting = signal(false);

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
      const request: CreateIssueRequest = {
        project_id: this.projectId(),
        title: this.title().trim(),
        description: this.description().trim() || undefined,
        type: this.type(),
        priority: this.priority(),
        status: 'todo', // Default status
      };

      await this.issueService.createIssue(request);

      this.toast.success('Issue created successfully!');
      this.modal.close();

      // Reset form
      this.title.set('');
      this.description.set('');
      this.type.set('task');
      this.priority.set('medium');
    } catch (error) {
      console.error('Failed to create issue:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to create issue. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
