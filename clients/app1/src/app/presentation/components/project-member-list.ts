import {
  Component,
  ChangeDetectionStrategy,
  input,
  computed,
  inject,
  ViewContainerRef,
  TemplateRef,
  ViewChild,
  effect,
} from '@angular/core';
import {
  Button,
  Icon,
  Dropdown,
  LoadingState,
  ErrorState,
  EmptyState,
  Table,
  TableColumn,
  Modal,
  ToastService,
} from 'shared-ui';
import {
  ProjectMembersService,
  ProjectMember,
} from '../../application/services/project-members.service';
import { AuthService } from '../../application/services/auth.service';
import { AddProjectMemberModal } from './add-project-member-modal';
import { ChangeProjectMemberRoleModal } from './change-project-member-role-modal';

@Component({
  selector: 'app-project-member-list',
  imports: [Button, Icon, Dropdown, LoadingState, ErrorState, EmptyState, Table],
  template: `
    <div class="project-member-list">
      <div class="project-member-list_header">
        <div>
          <h2 class="project-member-list_title">Members</h2>
          <p class="project-member-list_subtitle">Manage project members and their roles.</p>
        </div>
        @if (canAddMembers()) {
          <lib-button variant="primary" size="md" leftIcon="plus" (clicked)="handleAddMember()">
            Add Member
          </lib-button>
        }
      </div>

      <div class="project-member-list_content">
        @if (membersService.isLoading()) {
          <lib-loading-state message="Loading members..." />
        } @else if (membersService.hasError()) {
          <lib-error-state
            title="Failed to Load Members"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else if (members().length === 0) {
          <lib-empty-state
            title="No members yet"
            message="Add members to your project to collaborate together."
            icon="users"
            [actionLabel]="canAddMembers() ? 'Add Member' : ''"
            [actionIcon]="canAddMembers() ? 'plus' : undefined"
            (onAction)="handleAddMember()"
          />
        } @else {
          <lib-table
            [data]="members()"
            [columns]="columns()"
            [hasActions]="hasManageableMembers()"
            [trackByFn]="trackByMemberId"
            [hoverable]="true"
            [cellTemplate]="cellTemplate"
            [actionsTemplate]="actionsTemplate"
          />
        }
      </div>

      <!-- Templates -->
      <ng-template #cellTemplate let-member let-column="column">
        @if (column.key === 'member') {
          <div class="project-member-list_table-member">
            <div class="project-member-list_table-avatar">
              @if (member.avatar_url) {
                <img
                  [src]="member.avatar_url"
                  [alt]="member.user_name"
                  class="project-member-list_table-avatar-image"
                />
              } @else {
                <div class="project-member-list_table-avatar-placeholder">
                  {{ getInitials(member.user_name) }}
                </div>
              }
            </div>
            <div class="project-member-list_table-info">
              <div class="project-member-list_table-name">{{ member.user_name }}</div>
              <div class="project-member-list_table-email">{{ member.user_email }}</div>
            </div>
          </div>
        } @else if (column.key === 'role') {
          <span
            class="project-member-list_role-badge"
            [class]="'project-member-list_role-badge--' + member.role"
          >
            {{ getRoleLabel(member.role) }}
          </span>
        }
      </ng-template>

      <ng-template #actionsTemplate let-member>
        @if (canManageMember(member)) {
          <lib-button
            variant="ghost"
            size="sm"
            [iconOnly]="true"
            leftIcon="ellipsis-vertical"
            [libDropdown]="actionsDropdownTemplate"
            [position]="'below'"
            #actionsDropdown="libDropdown"
          >
          </lib-button>
          <ng-template #actionsDropdownTemplate>
            <div class="project-member-list_actions-menu">
              @if (canChangeRole(member)) {
                <lib-button
                  variant="ghost"
                  size="md"
                  class="project-member-list_action-item"
                  (clicked)="handleChangeRole(member, actionsDropdown)"
                >
                  <lib-icon name="user-cog" size="sm" class="project-member-list_action-icon" />
                  <span>Change Role</span>
                </lib-button>
              }
              @if (canRemoveMember(member)) {
                <lib-button
                  variant="ghost"
                  size="md"
                  class="project-member-list_action-item project-member-list_action-item--danger"
                  (clicked)="handleRemoveMember(member, actionsDropdown)"
                >
                  <lib-icon name="user-minus" size="sm" class="project-member-list_action-icon" />
                  <span>Remove</span>
                </lib-button>
              }
            </div>
          </ng-template>
        }
      </ng-template>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .project-member-list {
        @apply flex flex-col;
        @apply gap-6;
      }

      .project-member-list_header {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .project-member-list_title {
        @apply text-xl font-semibold mb-1;
        @apply text-text-primary;
        margin: 0;
      }

      .project-member-list_subtitle {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .project-member-list_content {
        @apply flex flex-col;
      }

      .project-member-list_table-member {
        @apply flex items-center;
        @apply gap-3;
      }

      .project-member-list_table-avatar {
        @apply w-10 h-10;
        @apply rounded-full;
        @apply overflow-hidden;
        @apply flex-shrink-0;
        @apply bg-bg-tertiary;
      }

      .project-member-list_table-avatar-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .project-member-list_table-avatar-placeholder {
        @apply w-full h-full;
        @apply flex items-center justify-center;
        @apply text-sm font-semibold;
        @apply text-text-primary;
      }

      .project-member-list_table-info {
        @apply flex flex-col;
        @apply min-w-0;
      }

      .project-member-list_table-name {
        @apply text-sm font-medium;
        @apply text-text-primary;
        @apply truncate;
      }

      .project-member-list_table-email {
        @apply text-xs;
        @apply text-text-secondary;
        @apply truncate;
      }

      .project-member-list_role-badge {
        @apply inline-flex items-center;
        @apply px-2.5 py-1;
        @apply rounded-full;
        @apply text-xs font-medium;
      }

      .project-member-list_role-badge--admin {
        @apply bg-primary-100;
        @apply text-primary-700;
      }

      .project-member-list_role-badge--member {
        @apply bg-gray-100;
        @apply text-gray-700;
      }

      .project-member-list_role-badge--viewer {
        @apply bg-gray-50;
        @apply text-gray-600;
      }

      .project-member-list_actions-menu {
        @apply py-1;
        min-width: 10rem;
      }

      .project-member-list_action-item {
        @apply w-full;
        @apply justify-start;
        @apply px-4 py-2;
      }

      .project-member-list_action-icon {
        @apply flex-shrink-0;
      }

      .project-member-list_action-item--danger {
        @apply text-error;
      }

      .project-member-list_action-item--danger:hover {
        @apply bg-error-50;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectMemberList {
  readonly membersService = inject(ProjectMembersService);
  readonly authService = inject(AuthService);
  readonly modal = inject(Modal);
  readonly toast = inject(ToastService);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly projectId = input.required<string>();

  readonly members = computed(() => this.membersService.members());
  readonly isLoading = computed(() => this.membersService.isLoading());
  readonly hasError = computed(() => this.membersService.hasError());
  readonly currentUserId = computed(() => this.authService.getUser()?.id || null);

  readonly errorMessage = computed(() => {
    const error = this.membersService.error();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading members.';
    }
    return 'An unknown error occurred.';
  });

  @ViewChild('cellTemplate') cellTemplate!: TemplateRef<{
    $implicit: ProjectMember;
    column: TableColumn<ProjectMember>;
    index: number;
  }>;
  @ViewChild('actionsTemplate') actionsTemplate!: TemplateRef<{
    $implicit: ProjectMember;
    index: number;
  }>;

  readonly columns = computed<TableColumn<ProjectMember>[]>(() => [
    {
      key: 'member',
      label: 'Member',
      width: '40%',
    },
    {
      key: 'role',
      label: 'Role',
      width: '20%',
    },
  ]);

  readonly canAddMembers = computed(() => {
    // For now, assume organization admins can add members
    // TODO: Check actual project admin role when available
    return true;
  });

  readonly hasManageableMembers = computed(() => {
    return this.members().some((member) => this.canManageMember(member));
  });

  // Members resource automatically loads when projectId changes via navigation service

  trackByMemberId = (member: ProjectMember): string => member.user_id;

  getInitials(name: string): string {
    const nameParts = name.split(' ');
    const initials = nameParts
      .map((part) => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
    return initials || 'U';
  }

  getRoleLabel(role: 'admin' | 'member' | 'viewer'): string {
    switch (role) {
      case 'admin':
        return 'Admin';
      case 'member':
        return 'Member';
      case 'viewer':
        return 'Viewer';
      default:
        return role;
    }
  }

  canManageMember(member: ProjectMember): boolean {
    // TODO: Check if current user is project admin
    // For now, allow management
    return true;
  }

  canChangeRole(member: ProjectMember): boolean {
    const currentId = this.currentUserId();
    // Can change role if not the current user
    return member.user_id !== currentId;
  }

  canRemoveMember(member: ProjectMember): boolean {
    const currentId = this.currentUserId();
    // Can remove if not the current user
    return member.user_id !== currentId;
  }

  handleAddMember(): void {
    this.modal.open(AddProjectMemberModal, this.viewContainerRef, {
      size: 'md',
      data: { projectId: this.projectId() },
    });
  }

  handleChangeRole(member: ProjectMember, dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.modal.open(ChangeProjectMemberRoleModal, this.viewContainerRef, {
      size: 'md',
      data: { projectId: this.projectId(), member },
    });
  }

  async handleRemoveMember(member: ProjectMember, dropdown: Dropdown): Promise<void> {
    dropdown.open.set(false);

    if (!confirm(`Are you sure you want to remove ${member.user_name} from this project?`)) {
      return;
    }

    try {
      await this.membersService.removeMember(this.projectId(), member.user_id);
      this.toast.success('Member removed successfully!');
    } catch (error) {
      console.error('Failed to remove member:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to remove member. Please try again.';
      this.toast.error(errorMessage);
    }
  }

  handleRetry(): void {
    this.membersService.reloadMembers();
  }
}
