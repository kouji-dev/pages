import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  ViewChild,
  effect,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input, TextEditor } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { IssueService, CreateIssueRequest } from '../../application/services/issue.service';
import { ProjectMembersService } from '../../application/services/project-members.service';

type IssueType = 'task' | 'bug' | 'story' | 'epic';
type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';
type IssuePriority = 'low' | 'medium' | 'high' | 'critical';

@Component({
  selector: 'app-create-issue-modal',
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
          <div class="create-issue-form_field">
            <label class="create-issue-form_label">Description</label>
            <lib-text-editor
              #descriptionEditor
              placeholder="Describe the issue in detail (optional)"
              [(ngModel)]="description"
              name="description"
              (htmlChange)="descriptionHtml.set($event)"
              [showToolbar]="true"
            />
          </div>
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
          <div class="create-issue-form_row">
            <div class="create-issue-form_field">
              <label class="create-issue-form_label">Assignee (optional)</label>
              <select
                class="create-issue-form_select"
                [value]="assigneeId() || ''"
                (change)="assigneeId.set($any($event.target).value || null)"
              >
                <option value="">Unassigned</option>
                @for (member of projectMembers(); track member.user_id) {
                  <option [value]="member.user_id">{{ member.user_name }}</option>
                }
              </select>
            </div>
            <div class="create-issue-form_field">
              <label class="create-issue-form_label">Due Date (optional)</label>
              <input
                type="date"
                class="create-issue-form_input"
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

      .create-issue-form_input {
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
  private readonly projectMembersService = inject(ProjectMembersService);

  readonly projectId = input.required<string>();

  readonly title = signal('');
  readonly description = signal('');
  readonly descriptionHtml = signal('');
  readonly type = signal<IssueType>('task');
  readonly priority = signal<IssuePriority>('medium');
  readonly assigneeId = signal<string | null>(null);
  readonly dueDate = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  @ViewChild('descriptionEditor') descriptionEditor?: TextEditor;

  // Load project members when projectId changes
  private readonly loadMembersEffect = effect(() => {
    const id = this.projectId();
    if (id) {
      this.projectMembersService.loadMembers(id);
    }
  });

  readonly projectMembers = computed(() => this.projectMembersService.members());

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
        description: this.descriptionHtml().trim() || undefined,
        type: this.type(),
        priority: this.priority(),
        status: 'todo', // Default status
        assignee_id: this.assigneeId() || undefined,
        due_date: this.dueDate() || undefined,
      };

      await this.issueService.createIssue(request);

      this.toast.success('Issue created successfully!');
      this.modal.close();

      // Reset form
      this.title.set('');
      this.description.set('');
      this.descriptionHtml.set('');
      this.type.set('task');
      this.priority.set('medium');
      this.assigneeId.set(null);
      this.dueDate.set(null);
      if (this.descriptionEditor) {
        this.descriptionEditor.setHtml('');
      }
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
