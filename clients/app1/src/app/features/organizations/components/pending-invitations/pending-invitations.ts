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
import { Button, Icon, LoadingState, ErrorState, EmptyState, Table, TableColumn } from 'shared-ui';
import { OrganizationInvitation } from '../../../../application/services/organization-invitations.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-pending-invitations',
  imports: [Button, Icon, LoadingState, ErrorState, EmptyState, Table, TranslatePipe],
  template: `
    <div class="pending-invitations">
      <div class="pending-invitations_header">
        <div>
          <h2 class="pending-invitations_title">{{ 'invitations.pendingTitle' | translate }}</h2>
          <p class="pending-invitations_subtitle">
            {{ 'invitations.pendingSubtitle' | translate }}
          </p>
        </div>
        @if (canSendInvitations()) {
          <lib-button
            variant="primary"
            size="md"
            leftIcon="mail"
            (clicked)="handleSendInvitation()"
          >
            {{ 'invitations.sendInvitation' | translate }}
          </lib-button>
        }
      </div>

      <div class="pending-invitations_content">
        @if (isLoading()) {
          <lib-loading-state [message]="'invitations.loading' | translate" />
        } @else if (hasError()) {
          <lib-error-state
            [title]="'invitations.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else if (invitations().length === 0) {
          <lib-empty-state
            [title]="'invitations.noPending' | translate"
            [message]="'invitations.noPendingDescription' | translate"
            icon="mail"
            [actionLabel]="canSendInvitations() ? ('invitations.sendInvitation' | translate) : ''"
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
                <span>{{ 'invitations.expiringSoon' | translate }}</span>
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
            [title]="'invitations.cancelInvitation' | translate"
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
        @apply text-foreground;
        margin: 0;
      }

      .pending-invitations_subtitle {
        @apply text-sm;
        @apply text-muted-foreground;
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
        @apply text-foreground;
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
        @apply bg-primary/20;
        @apply text-primary;
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
        @apply text-foreground;
      }

      .pending-invitations_table-date-relative {
        @apply text-xs;
        @apply text-muted-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PendingInvitations {
  private readonly translateService = inject(TranslateService);

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
      label: this.translateService.instant('invitations.email'),
      width: '30%',
    },
    {
      key: 'role',
      label: this.translateService.instant('members.role'),
      width: '20%',
    },
    {
      key: 'expires_at',
      label: this.translateService.instant('invitations.expires'),
      width: '30%',
    },
  ]);

  trackByInvitationId = (invitation: OrganizationInvitation): string => invitation.id;

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
      return this.translateService.instant('invitations.expired');
    } else if (diffInDays === 0) {
      return this.translateService.instant('invitations.expiresToday');
    } else if (diffInDays === 1) {
      return this.translateService.instant('invitations.expiresTomorrow');
    } else if (diffInDays <= 7) {
      return this.translateService.instant('invitations.expiresInDays', { count: diffInDays });
    } else {
      const diffInWeeks = Math.floor(diffInDays / 7);
      return this.translateService.instant('invitations.expiresInWeeks', { count: diffInWeeks });
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
