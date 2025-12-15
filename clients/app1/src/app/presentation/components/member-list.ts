import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  computed,
  TemplateRef,
  ViewChild,
  inject,
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
} from 'shared-ui';
import { OrganizationMember } from '../../application/services/organization-members.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-member-list',
  imports: [Button, Icon, Dropdown, LoadingState, ErrorState, EmptyState, Table, TranslatePipe],
  template: `
    <div class="member-list">
      <div class="member-list_header">
        <div>
          <h2 class="member-list_title">{{ 'members.title' | translate }}</h2>
          <p class="member-list_subtitle">{{ 'members.subtitle' | translate }}</p>
        </div>
        @if (canAddMembers()) {
          <lib-button variant="primary" size="md" leftIcon="plus" (clicked)="handleAddMember()">
            {{ 'members.addMember' | translate }}
          </lib-button>
        }
      </div>

      <div class="member-list_content">
        @if (isLoading()) {
          <lib-loading-state [message]="'members.loadingMembers' | translate" />
        } @else if (hasError()) {
          <lib-error-state
            [title]="'members.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else if (members().length === 0) {
          <lib-empty-state
            [title]="'members.noMembers' | translate"
            [message]="'members.noMembersDescription' | translate"
            icon="users"
            [actionLabel]="canAddMembers() ? ('members.addMember' | translate) : ''"
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
          <div class="member-list_table-member">
            <div class="member-list_table-avatar">
              @if (member.avatar_url) {
                <img
                  [src]="member.avatar_url"
                  [alt]="member.user_name"
                  class="member-list_table-avatar-image"
                />
              } @else {
                <div class="member-list_table-avatar-placeholder">
                  {{ getInitials(member.user_name) }}
                </div>
              }
            </div>
            <div class="member-list_table-info">
              <div class="member-list_table-name">{{ member.user_name }}</div>
              <div class="member-list_table-email">{{ member.user_email }}</div>
            </div>
          </div>
        } @else if (column.key === 'role') {
          <span class="member-list_role-badge" [class]="'member-list_role-badge--' + member.role">
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
            <div class="member-list_actions-menu">
              @if (canChangeRole(member)) {
                <lib-button
                  variant="ghost"
                  size="md"
                  class="member-list_action-item"
                  (clicked)="handleChangeRole(member, actionsDropdown)"
                >
                  <lib-icon name="user-cog" size="sm" class="member-list_action-icon" />
                  <span>{{ 'members.changeRole' | translate }}</span>
                </lib-button>
              }
              @if (canRemoveMember(member)) {
                <lib-button
                  variant="ghost"
                  size="md"
                  class="member-list_action-item member-list_action-item--danger"
                  (clicked)="handleRemoveMember(member, actionsDropdown)"
                >
                  <lib-icon name="user-minus" size="sm" class="member-list_action-icon" />
                  <span>{{ 'members.remove' | translate }}</span>
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

      .member-list {
        @apply flex flex-col;
        @apply gap-6;
      }

      .member-list_header {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .member-list_title {
        @apply text-xl font-semibold mb-1;
        @apply text-text-primary;
        margin: 0;
      }

      .member-list_subtitle {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .member-list_content {
        @apply flex flex-col;
      }

      .member-list_table-member {
        @apply flex items-center;
        @apply gap-3;
      }

      .member-list_table-avatar {
        @apply w-10 h-10;
        @apply rounded-full;
        @apply overflow-hidden;
        @apply flex-shrink-0;
        @apply bg-bg-tertiary;
      }

      .member-list_table-avatar-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .member-list_table-avatar-placeholder {
        @apply w-full h-full;
        @apply flex items-center justify-center;
        @apply text-sm font-semibold;
        @apply text-text-primary;
      }

      .member-list_table-info {
        @apply flex flex-col;
        @apply min-w-0;
      }

      .member-list_table-name {
        @apply text-sm font-medium;
        @apply text-text-primary;
        @apply truncate;
      }

      .member-list_table-email {
        @apply text-xs;
        @apply text-text-secondary;
        @apply truncate;
      }

      .member-list_role-badge {
        @apply inline-flex items-center;
        @apply px-2.5 py-1;
        @apply rounded-full;
        @apply text-xs font-medium;
      }

      .member-list_role-badge--admin {
        @apply bg-primary-100;
        @apply text-primary-700;
      }

      .member-list_role-badge--member {
        @apply bg-gray-100;
        @apply text-gray-700;
      }

      .member-list_role-badge--viewer {
        @apply bg-gray-50;
        @apply text-gray-600;
      }

      .member-list_actions-menu {
        @apply py-1;
        min-width: 10rem;
      }

      .member-list_action-item {
        @apply w-full;
        @apply justify-start;
        @apply px-4 py-2;
      }

      .member-list_action-icon {
        @apply flex-shrink-0;
      }

      .member-list_action-item--danger {
        @apply text-error;
      }

      .member-list_action-item--danger:hover {
        @apply bg-error-50;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MemberList {
  private readonly translateService = inject(TranslateService);

  readonly members = input.required<OrganizationMember[]>();
  readonly isLoading = input.required<boolean>();
  readonly hasError = input.required<boolean>();
  readonly errorMessage = input<string>('');
  readonly canAddMembers = input<boolean>(true);
  readonly currentUserId = input<string | null>(null);
  readonly currentUserRole = input<'admin' | 'member' | 'viewer' | null>(null);

  readonly onAddMember = output<void>();
  readonly onChangeRole = output<OrganizationMember>();
  readonly onRemoveMember = output<OrganizationMember>();
  readonly onRetry = output<void>();

  @ViewChild('cellTemplate') cellTemplate!: TemplateRef<{
    $implicit: OrganizationMember;
    column: TableColumn<OrganizationMember>;
    index: number;
  }>;
  @ViewChild('actionsTemplate') actionsTemplate!: TemplateRef<{
    $implicit: OrganizationMember;
    index: number;
  }>;

  readonly columns = computed<TableColumn<OrganizationMember>[]>(() => [
    {
      key: 'member',
      label: this.translateService.instant('members.title'),
      width: '40%',
    },
    {
      key: 'role',
      label: this.translateService.instant('members.role'),
      width: '20%',
    },
  ]);

  readonly hasManageableMembers = computed(() => {
    return this.members().some((member) => this.canManageMember(member));
  });

  trackByMemberId = (member: OrganizationMember): string => member.user_id;

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
        return this.translateService.instant('members.admin');
      case 'member':
        return this.translateService.instant('members.member');
      case 'viewer':
        return this.translateService.instant('members.viewer');
      default:
        return role;
    }
  }

  canManageMember(member: OrganizationMember): boolean {
    const currentRole = this.currentUserRole();
    // Only admins can manage members
    return currentRole === 'admin';
  }

  canChangeRole(member: OrganizationMember): boolean {
    const currentRole = this.currentUserRole();
    const currentId = this.currentUserId();
    // Admins can change roles, but can't change their own role
    return currentRole === 'admin' && member.user_id !== currentId;
  }

  canRemoveMember(member: OrganizationMember): boolean {
    const currentRole = this.currentUserRole();
    const currentId = this.currentUserId();
    // Admins can remove members, or users can remove themselves
    return currentRole === 'admin' || member.user_id === currentId;
  }

  handleAddMember(): void {
    this.onAddMember.emit();
  }

  handleChangeRole(member: OrganizationMember, dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.onChangeRole.emit(member);
  }

  handleRemoveMember(member: OrganizationMember, dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.onRemoveMember.emit(member);
  }

  handleRetry(): void {
    this.onRetry.emit();
  }
}
