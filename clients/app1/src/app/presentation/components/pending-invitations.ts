import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  computed,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import { Button, Icon, LoadingState, ErrorState, EmptyState, Table, TableColumn } from 'shared-ui';
import { OrganizationInvitation } from '../../application/services/organization-invitations.service';

@Component({
  selector: 'app-pending-invitations',
  imports: [Button, Icon, LoadingState, ErrorState, EmptyState, Table],
  template: `
    <div class="pending-invitations">
      <div class="pending-invitations_header">
        <div>
          <h2 class="pending-invitations_title">Pending Invitations</h2>
          <p class="pending-invitations_subtitle">Invitations that haven't been accepted yet.</p>
        </div>
        @if (canSendInvitations()) {
          <lib-button
            variant="primary"
            size="md"
            leftIcon="mail"
            (clicked)="handleSendInvitation()"
          >
            Send Invitation
          </lib-button>
        }
      </div>

      <div class="pending-invitations_content">
        @if (isLoading()) {
          <lib-loading-state message="Loading invitations..." />
        } @else if (hasError()) {
          <lib-error-state
            title="Failed to Load Invitations"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else if (invitations().length === 0) {
          <lib-empty-state
            title="No pending invitations"
            message="Invite people to join your organization by sending them an invitation."
            icon="mail"
            [actionLabel]="canSendInvitations() ? 'Send Invitation' : ''"
            [actionIcon]="canSendInvitations() ? 'mail' : undefined"
            (onAction)="handleSendInvitation()"
          />
        } @else {
          <lib-table
            [data]="invitations()"
            [columns]="columns()"
            [hasActions]="canCancelInvitations()"
            [trackByFn]="trackByInvitationId"
            [hoverable]="true"
            [cellTemplate]="cellTemplate"
            [actionsTemplate]="actionsTemplate"
          />
        }
      </div>

      <!-- Templates -->
      <ng-template #cellTemplate let-invitation let-column="column">
        @if (column.key === 'email') {
          <div class="pending-invitations_table-email">
            <div class="pending-invitations_table-email-address">{{ invitation.email }}</div>
            @if (isExpiringSoon(invitation)) {
              <div class="pending-invitations_table-expiring-warning">
                <lib-icon name="clock" size="xs" />
                <span>Expiring soon</span>
              </div>
            }
          </div>
        } @else if (column.key === 'role') {
          <span
            class="pending-invitations_role-badge"
            [class]="'pending-invitations_role-badge--' + invitation.role"
          >
            {{ getRoleLabel(invitation.role) }}
          </span>
        } @else if (column.key === 'expires_at') {
          <div class="pending-invitations_table-date">
            <div class="pending-invitations_table-date-value">
              {{ formatDate(invitation.expires_at) }}
            </div>
            <div class="pending-invitations_table-date-relative">
              {{ formatRelativeDate(invitation.expires_at) }}
            </div>
          </div>
        }
      </ng-template>

      <ng-template #actionsTemplate let-invitation>
        @if (canCancelInvitation(invitation)) {
          <lib-button
            variant="ghost"
            size="sm"
            [iconOnly]="true"
            leftIcon="x"
            (clicked)="handleCancelInvitation(invitation)"
            [title]="'Cancel invitation'"
          >
          </lib-button>
        }
      </ng-template>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .pending-invitations {
        @apply flex flex-col;
        @apply gap-6;
      }

      .pending-invitations_header {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .pending-invitations_title {
        @apply text-xl font-semibold mb-1;
        @apply text-text-primary;
        margin: 0;
      }

      .pending-invitations_subtitle {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .pending-invitations_content {
        @apply flex flex-col;
      }

      .pending-invitations_table-email {
        @apply flex flex-col;
        @apply gap-1;
      }

      .pending-invitations_table-email-address {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .pending-invitations_table-expiring-warning {
        @apply flex items-center gap-1;
        @apply text-xs;
        @apply text-warning;
      }

      .pending-invitations_role-badge {
        @apply inline-flex items-center;
        @apply px-2.5 py-1;
        @apply rounded-full;
        @apply text-xs font-medium;
      }

      .pending-invitations_role-badge--admin {
        @apply bg-primary-100;
        @apply text-primary-700;
      }

      .pending-invitations_role-badge--member {
        @apply bg-gray-100;
        @apply text-gray-700;
      }

      .pending-invitations_role-badge--viewer {
        @apply bg-gray-50;
        @apply text-gray-600;
      }

      .pending-invitations_table-date {
        @apply flex flex-col;
        @apply gap-1;
      }

      .pending-invitations_table-date-value {
        @apply text-sm;
        @apply text-text-primary;
      }

      .pending-invitations_table-date-relative {
        @apply text-xs;
        @apply text-text-secondary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PendingInvitations {
  readonly invitations = input.required<OrganizationInvitation[]>();
  readonly isLoading = input.required<boolean>();
  readonly hasError = input.required<boolean>();
  readonly errorMessage = input<string>('');
  readonly canSendInvitations = input<boolean>(true);
  readonly canCancelInvitations = input<boolean>(true);

  readonly onSendInvitation = output<void>();
  readonly onCancelInvitation = output<OrganizationInvitation>();
  readonly onRetry = output<void>();

  @ViewChild('cellTemplate') cellTemplate!: TemplateRef<{
    $implicit: OrganizationInvitation;
    column: TableColumn<OrganizationInvitation>;
    index: number;
  }>;
  @ViewChild('actionsTemplate') actionsTemplate!: TemplateRef<{
    $implicit: OrganizationInvitation;
    index: number;
  }>;

  readonly columns = computed<TableColumn<OrganizationInvitation>[]>(() => [
    {
      key: 'email',
      label: 'Email',
      width: '30%',
    },
    {
      key: 'role',
      label: 'Role',
      width: '20%',
    },
    {
      key: 'expires_at',
      label: 'Expires',
      width: '30%',
    },
  ]);

  trackByInvitationId = (invitation: OrganizationInvitation): string => invitation.id;

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

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  formatRelativeDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = date.getTime() - now.getTime();
    const diffInDays = Math.ceil(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInDays < 0) {
      return 'Expired';
    } else if (diffInDays === 0) {
      return 'Expires today';
    } else if (diffInDays === 1) {
      return 'Expires tomorrow';
    } else if (diffInDays <= 7) {
      return `Expires in ${diffInDays} days`;
    } else {
      const diffInWeeks = Math.floor(diffInDays / 7);
      return `Expires in ${diffInWeeks} ${diffInWeeks === 1 ? 'week' : 'weeks'}`;
    }
  }

  isExpiringSoon(invitation: OrganizationInvitation): boolean {
    const date = new Date(invitation.expires_at);
    const now = new Date();
    const diffInMs = date.getTime() - now.getTime();
    const diffInDays = Math.ceil(diffInMs / (1000 * 60 * 60 * 24));
    return diffInDays >= 0 && diffInDays <= 2;
  }

  canCancelInvitation(invitation: OrganizationInvitation): boolean {
    return this.canCancelInvitations();
  }

  handleSendInvitation(): void {
    this.onSendInvitation.emit();
  }

  handleCancelInvitation(invitation: OrganizationInvitation): void {
    this.onCancelInvitation.emit(invitation);
  }

  handleRetry(): void {
    this.onRetry.emit();
  }
}
