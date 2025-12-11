import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  effect,
  ViewChild,
  model,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input, TextEditor, Select, SelectOption } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { IssueService, UpdateIssueRequest, Issue } from '../../application/services/issue.service';
import { ProjectMembersService } from '../../application/services/project-members.service';
import { getIssuePriorityConfig, type IssuePriority } from '../helpers/issue-helpers';

type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';

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
    Select,
    FormsModule,
    CommonModule,
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
              <lib-select
                label="Status"
                [options]="statusSelectOptions()"
                [(model)]="statusModel"
                [placeholder]="'Select status...'"
              />
            </div>
            <div class="edit-issue-form_field">
              <lib-select
                label="Priority"
                [options]="prioritySelectOptions()"
                [(model)]="priorityModel"
                [placeholder]="'Select priority...'"
              />
            </div>
          </div>
          <div class="edit-issue-form_row">
            <div class="edit-issue-form_field">
              <lib-select
                label="Assignee"
                [options]="assigneeSelectOptions()"
                [(model)]="assigneeModel"
                [placeholder]="'Unassigned'"
              />
            </div>
            <div class="edit-issue-form_field">
              <label class="edit-issue-form_label">Due Date</label>
              <input
                type="date"
                class="edit-issue-form_input"
                [value]="dueDate() || ''"
                (change)="dueDate.set($any($event.target).value || null)"
              />
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

      .edit-issue-form_input {
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
  private readonly projectMembersService = inject(ProjectMembersService);

  readonly issueId = input.required<string>();
  readonly issue = input.required<Issue>();

  readonly title = signal('');
  readonly description = signal('');
  readonly descriptionHtml = signal('');
  readonly status = signal<IssueStatus>('todo');
  readonly priority = signal<IssuePriority>('medium');
  readonly assigneeId = signal<string | null>(null);
  readonly dueDate = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  // Model signals for lib-select two-way binding
  readonly statusModel = model<IssueStatus>('todo');
  readonly priorityModel = model<IssuePriority>('medium');
  readonly assigneeModel = model<string | null>(null);

  // Sync model signals with regular signals (model -> signal for user changes)
  private readonly syncStatusEffect = effect(() => {
    this.status.set(this.statusModel());
  });

  private readonly syncPriorityEffect = effect(() => {
    this.priority.set(this.priorityModel());
  });

  private readonly syncAssigneeEffect = effect(() => {
    this.assigneeId.set(this.assigneeModel());
  });

  @ViewChild('descriptionEditor') descriptionEditor?: TextEditor;

  // Load project members when issue changes
  private readonly loadMembersEffect = effect(() => {
    const issue = this.issue();
    if (issue?.project_id) {
      this.projectMembersService.loadMembers(issue.project_id);
    }
  });

  readonly projectMembers = computed(() => this.projectMembersService.members());

  readonly statusSelectOptions = computed<SelectOption<IssueStatus>[]>(() => [
    { value: 'todo', label: 'To Do' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'done', label: 'Done' },
    { value: 'cancelled', label: 'Cancelled' },
  ]);

  readonly prioritySelectOptions = computed<SelectOption<IssuePriority>[]>(() => {
    return (['low', 'medium', 'high', 'critical'] as IssuePriority[]).map((value) => {
      const config = getIssuePriorityConfig(value);
      return {
        value,
        label: config.label,
        icon: config.icon,
        iconColor: config.iconColor,
      };
    });
  });

  readonly assigneeSelectOptions = computed<SelectOption<string | null>[]>(() => {
    const options: SelectOption<string | null>[] = [{ value: null, label: 'Unassigned' }];
    return options.concat(
      this.projectMembers().map((member) => ({
        value: member.user_id,
        label: member.user_name,
      })),
    );
  });

  private readonly initializeEffect = effect(
    () => {
      const issue = this.issue();
      if (issue) {
        this.title.set(issue.title);
        const desc = issue.description || '';
        this.description.set(desc);
        this.descriptionHtml.set(desc);
        this.status.set(issue.status);
        this.statusModel.set(issue.status);
        this.priority.set(issue.priority);
        this.priorityModel.set(issue.priority);
        this.assigneeId.set(issue.assignee_id || null);
        this.assigneeModel.set(issue.assignee_id || null);
        // Format due_date for date input (YYYY-MM-DD)
        if (issue.due_date) {
          const date = new Date(issue.due_date);
          const formattedDate = date.toISOString().split('T')[0];
          this.dueDate.set(formattedDate);
        } else {
          this.dueDate.set(null);
        }
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
        assignee_id: this.assigneeId() || undefined,
        due_date: this.dueDate() || undefined,
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
