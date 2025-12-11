import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  ViewChild,
  effect,
  model,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input, TextEditor, Icon, Select, SelectOption } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { IssueService, CreateIssueRequest } from '../../application/services/issue.service';
import { ProjectMembersService } from '../../application/services/project-members.service';
import {
  getIssueTypeConfig,
  getIssuePriorityConfig,
  type IssueType,
  type IssuePriority,
} from '../helpers/issue-helpers';

type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';

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
    Select,
    FormsModule,
    CommonModule,
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
              <lib-select
                label="Type"
                [options]="typeSelectOptions()"
                [(model)]="typeModel"
                [placeholder]="'Select type...'"
              />
            </div>
            <div class="create-issue-form_field">
              <lib-select
                label="Priority"
                [options]="prioritySelectOptions()"
                [(model)]="priorityModel"
                [placeholder]="'Select priority...'"
              />
            </div>
          </div>
          <div class="create-issue-form_row">
            <div class="create-issue-form_field">
              <lib-select
                label="Assignee (optional)"
                [options]="assigneeSelectOptions()"
                [(model)]="assigneeModel"
                [placeholder]="'Unassigned'"
              />
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

  // Model signals for lib-select two-way binding
  readonly typeModel = model<IssueType>('task');
  readonly priorityModel = model<IssuePriority>('medium');
  readonly assigneeModel = model<string | null>(null);

  // Sync model signals with regular signals
  private readonly syncTypeEffect = effect(() => {
    this.type.set(this.typeModel());
  });

  private readonly syncPriorityEffect = effect(() => {
    this.priority.set(this.priorityModel());
  });

  private readonly syncAssigneeEffect = effect(() => {
    this.assigneeId.set(this.assigneeModel());
  });

  @ViewChild('descriptionEditor') descriptionEditor?: TextEditor;

  readonly typeConfig = computed(() => getIssueTypeConfig(this.type()));
  readonly priorityConfig = computed(() => getIssuePriorityConfig(this.priority()));

  readonly typeIconClasses = computed(() => {
    const config = this.typeConfig();
    return {
      [config.textColor]: true,
    };
  });

  getTypeIconClasses(type: IssueType): Record<string, boolean> {
    const config = getIssueTypeConfig(type);
    return {
      [config.textColor]: true,
    };
  }

  getPriorityIconClasses(priority: IssuePriority): Record<string, boolean> {
    const config = getIssuePriorityConfig(priority);
    return {
      [config.iconColor]: true,
    };
  }

  readonly priorityIconClasses = computed(() => {
    const config = this.priorityConfig();
    return {
      [config.iconColor]: true,
    };
  });

  readonly typeOptions = computed(() => {
    return (['task', 'bug', 'story', 'epic'] as IssueType[]).map((value) => ({
      value,
      config: getIssueTypeConfig(value),
    }));
  });

  readonly priorityOptions = computed(() => {
    return (['low', 'medium', 'high', 'critical'] as IssuePriority[]).map((value) => ({
      value,
      config: getIssuePriorityConfig(value),
    }));
  });

  readonly typeSelectOptions = computed<SelectOption<IssueType>[]>(() => {
    return this.typeOptions().map((opt) => ({
      value: opt.value,
      label: opt.config.label,
      icon: opt.config.icon,
      iconColor: opt.config.textColor,
    }));
  });

  readonly prioritySelectOptions = computed<SelectOption<IssuePriority>[]>(() => {
    return this.priorityOptions().map((opt) => ({
      value: opt.value,
      label: opt.config.label,
      icon: opt.config.icon,
      iconColor: opt.config.iconColor,
    }));
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
      this.typeModel.set('task');
      this.priority.set('medium');
      this.priorityModel.set('medium');
      this.assigneeId.set(null);
      this.assigneeModel.set(null);
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
