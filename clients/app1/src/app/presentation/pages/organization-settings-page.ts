import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  ViewContainerRef,
  effect,
} from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Button, Icon, Input, LoadingState, ErrorState, Modal } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { OrganizationService, Organization } from '../../application/services/organization.service';
import { DeleteOrganizationModal } from '../components/delete-organization-modal';
import { MemberList } from '../components/member-list';
import { AddMemberModal } from '../components/add-member-modal';
import { ChangeRoleModal } from '../components/change-role-modal';
import { PendingInvitations } from '../components/pending-invitations';
import { InviteMemberModal } from '../components/invite-member-modal';
import {
  OrganizationMembersService,
  OrganizationMember,
} from '../../application/services/organization-members.service';
import {
  OrganizationInvitationsService,
  OrganizationInvitation,
} from '../../application/services/organization-invitations.service';
import { AuthService } from '../../application/services/auth.service';

@Component({
  selector: 'app-organization-settings-page',
  imports: [
    Button,
    Icon,
    Input,
    LoadingState,
    ErrorState,
    RouterLink,
    MemberList,
    PendingInvitations,
  ],
  template: `
    <div class="org-settings-page">
      <div class="org-settings-page_header">
        <div class="org-settings-page_header-content">
          <div>
            <a routerLink="/app/organizations" class="org-settings-page_back-link">
              <lib-icon name="arrow-left" size="sm" />
              <span>Back to Organizations</span>
            </a>
            <h1 class="org-settings-page_title">Organization Settings</h1>
            @if (organization()) {
              <p class="org-settings-page_subtitle">{{ organization()!.name }}</p>
            }
          </div>
        </div>
      </div>

      <div class="org-settings-page_content">
        @if (isLoading()) {
          <lib-loading-state message="Loading organization..." />
        } @else if (error()) {
          <lib-error-state
            title="Failed to Load Organization"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else if (!organization()) {
          <lib-error-state
            title="Organization Not Found"
            message="The organization you're looking for doesn't exist or you don't have access to it."
            [showRetry]="false"
          />
        } @else {
          <div class="org-settings-page_container">
            <!-- Organization Details Form -->
            <div class="org-settings-page_section">
              <h2 class="org-settings-page_section-title">Organization Details</h2>
              <form class="org-settings-page_form" (ngSubmit)="handleSave()">
                <lib-input
                  label="Organization Name"
                  placeholder="Enter organization name"
                  [(model)]="name"
                  [required]="true"
                  [errorMessage]="nameError()"
                  helperText="The display name for your organization"
                />
                <lib-input
                  label="Description"
                  type="textarea"
                  placeholder="Describe your organization (optional)"
                  [(model)]="description"
                  [rows]="4"
                  helperText="Optional description of your organization"
                />
                <div class="org-settings-page_form-actions">
                  <lib-button
                    variant="primary"
                    type="submit"
                    [loading]="isSaving()"
                    [disabled]="!isFormValid() || !hasChanges()"
                  >
                    Save Changes
                  </lib-button>
                  <lib-button
                    variant="secondary"
                    (clicked)="handleReset()"
                    [disabled]="!hasChanges() || isSaving()"
                  >
                    Cancel
                  </lib-button>
                </div>
              </form>
            </div>

            <!-- Members Section -->
            @if (organizationId()) {
              <div class="org-settings-page_section">
                <app-member-list
                  [members]="membersService.members()"
                  [isLoading]="membersService.isLoading()"
                  [hasError]="membersService.hasError()"
                  [errorMessage]="membersErrorMessage()"
                  [canAddMembers]="canManageMembers()"
                  [currentUserId]="currentUserId()"
                  [currentUserRole]="currentUserRole()"
                  (onAddMember)="handleAddMember()"
                  (onChangeRole)="handleChangeRole($event)"
                  (onRemoveMember)="handleRemoveMember($event)"
                  (onRetry)="handleMembersRetry()"
                />
              </div>
            }

            <!-- Pending Invitations Section -->
            @if (organizationId() && canManageMembers()) {
              <div class="org-settings-page_section">
                <app-pending-invitations
                  [invitations]="invitationsService.invitations()"
                  [isLoading]="invitationsService.isLoading()"
                  [hasError]="invitationsService.hasError()"
                  [errorMessage]="invitationsErrorMessage()"
                  [canSendInvitations]="canManageMembers()"
                  [canCancelInvitations]="canManageMembers()"
                  (onSendInvitation)="handleSendInvitation()"
                  (onCancelInvitation)="handleCancelInvitation($event)"
                  (onRetry)="handleInvitationsRetry()"
                />
              </div>
            }

            <!-- Danger Zone -->
            <div class="org-settings-page_section org-settings-page_section--danger">
              <h2 class="org-settings-page_section-title">Danger Zone</h2>
              <div class="org-settings-page_danger-content">
                <div>
                  <h3 class="org-settings-page_danger-title">Delete Organization</h3>
                  <p class="org-settings-page_danger-description">
                    Once you delete an organization, there is no going back. This will permanently
                    delete the organization and all associated data.
                  </p>
                </div>
                <lib-button
                  variant="danger"
                  (clicked)="handleDeleteClick()"
                  [disabled]="isDeleting()"
                >
                  Delete Organization
                </lib-button>
              </div>
            </div>
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .org-settings-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .org-settings-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .org-settings-page_header-content {
        @apply max-w-4xl mx-auto;
      }

      .org-settings-page_back-link {
        @apply inline-flex items-center gap-2;
        @apply text-sm font-medium mb-4;
        @apply text-primary-500;
        text-decoration: none;
        @apply transition-colors;
        @apply hover:opacity-80;
      }

      .org-settings-page_title {
        @apply text-3xl font-bold mb-2;
        @apply text-text-primary;
        margin: 0;
      }

      .org-settings-page_subtitle {
        @apply text-base;
        @apply text-text-secondary;
        margin: 0;
      }

      .org-settings-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .org-settings-page_container {
        @apply max-w-4xl mx-auto;
        @apply flex flex-col;
        @apply gap-8;
      }

      .org-settings-page_section {
        @apply flex flex-col;
        @apply gap-6;
        @apply p-6;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
      }

      .org-settings-page_section--danger {
        @apply border-error;
        @apply bg-error-50;
      }

      .org-settings-page_section-title {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .org-settings-page_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .org-settings-page_form-actions {
        @apply flex items-center;
        @apply gap-3;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .org-settings-page_danger-content {
        @apply flex items-start justify-between;
        @apply gap-6;
        @apply flex-wrap;
      }

      .org-settings-page_danger-title {
        @apply text-lg font-semibold mb-2;
        @apply text-text-primary;
        margin: 0;
      }

      .org-settings-page_danger-description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
        @apply max-w-md;
      }

      .org-settings-page_delete-warning {
        @apply text-sm font-medium;
        @apply text-error;
        margin: 1rem 0 0 0;
      }

      .org-settings-page_delete-warning ul {
        @apply list-disc list-inside;
        @apply mt-2 mb-4;
        @apply text-sm;
        @apply text-text-secondary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationSettingsPage {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly organizationService = inject(OrganizationService);
  readonly membersService = inject(OrganizationMembersService);
  readonly invitationsService = inject(OrganizationInvitationsService);
  private readonly authService = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);
  private readonly viewContainerRef = inject(ViewContainerRef);

  readonly name = signal('');
  readonly description = signal('');
  readonly isSaving = signal(false);
  readonly isDeleting = signal(false);

  readonly organizationId = computed(() => {
    const id = this.route.snapshot.paramMap.get('id');
    return id || null;
  });

  // Use service's current organization (computed from resource)
  readonly organization = this.organizationService.currentOrganization;
  readonly isLoading = this.organizationService.isFetchingOrganization;
  readonly error = computed(() => {
    const err = this.organizationService.organizationError();
    return err
      ? err instanceof Error
        ? err
        : new Error('Failed to load organization')
      : undefined;
  });

  readonly nameError = computed(() => {
    const value = this.name();
    if (!value.trim()) {
      return 'Organization name is required';
    }
    if (value.trim().length < 3) {
      return 'Organization name must be at least 3 characters';
    }
    return '';
  });

  readonly isFormValid = computed(() => {
    return !this.nameError() && this.name().trim().length > 0;
  });

  readonly hasChanges = computed(() => {
    const org = this.organization();
    if (!org) {
      return false;
    }
    return (
      this.name().trim() !== org.name ||
      (this.description().trim() || '') !== (org.description || '')
    );
  });

  readonly errorMessage = computed(() => {
    const err = this.error();
    if (err) {
      return err instanceof Error
        ? err.message
        : 'An error occurred while loading the organization.';
    }
    return 'An unknown error occurred.';
  });

  readonly currentUserId = computed(() => {
    return this.authService.currentUser()?.id || null;
  });

  readonly currentUserRole = computed<'admin' | 'member' | 'viewer' | null>(() => {
    const userId = this.currentUserId();
    const members = this.membersService.members();
    if (!userId || members.length === 0) {
      return null;
    }
    const member = members.find((m) => m.user_id === userId);
    return member?.role || null;
  });

  readonly canManageMembers = computed(() => {
    return this.currentUserRole() === 'admin';
  });

  readonly membersErrorMessage = computed(() => {
    const error = this.membersService.error();
    return error instanceof Error ? error.message : 'An unknown error occurred.';
  });

  readonly invitationsErrorMessage = computed(() => {
    const error = this.invitationsService.error();
    return error instanceof Error ? error.message : 'An unknown error occurred.';
  });

  // Effects declared as instance variables (not in constructor or ngOnInit)
  private readonly loadOrganizationEffect = effect(() => {
    const id = this.organizationId();
    if (id) {
      this.organizationService.fetchOrganization(id);
      this.membersService.loadMembers(id);
    }
  });

  private readonly loadInvitationsEffect = effect(() => {
    const id = this.organizationId();
    const canManage = this.canManageMembers();
    if (id && canManage) {
      this.invitationsService.loadInvitations(id);
    }
  });

  private readonly initializeFormEffect = effect(
    () => {
      const org = this.organization();
      if (org) {
        this.name.set(org.name);
        this.description.set(org.description || '');
      }
    },
    { allowSignalWrites: true },
  );

  handleSave(): void {
    if (!this.isFormValid() || !this.hasChanges()) {
      return;
    }

    const org = this.organization();
    if (!org) {
      return;
    }

    this.isSaving.set(true);

    this.organizationService
      .updateOrganization(org.id, {
        name: this.name().trim(),
        description: this.description().trim() || undefined,
      })
      .then(() => {
        this.toast.success('Organization updated successfully!');
        // Reload organization to get updated data
        this.organizationService.fetchOrganization(org.id);
      })
      .catch((error) => {
        console.error('Failed to update organization:', error);
        this.toast.error('Failed to update organization. Please try again.');
      })
      .finally(() => {
        this.isSaving.set(false);
      });
  }

  handleReset(): void {
    const org = this.organization();
    if (org) {
      this.name.set(org.name);
      this.description.set(org.description || '');
    }
  }

  handleDeleteClick(): void {
    const org = this.organization();
    if (!org) {
      return;
    }

    this.modal
      .open<{ confirmed: boolean; organizationId?: string; error?: any }>(
        DeleteOrganizationModal,
        this.viewContainerRef,
        {
          size: 'md',
          data: {
            organization: org,
          },
        },
      )
      .subscribe((result) => {
        if (result?.confirmed && result?.organizationId) {
          this.handleDeleteConfirm(result.organizationId);
        }
      });
  }

  async handleDeleteConfirm(organizationId: string): Promise<void> {
    try {
      await this.organizationService.deleteOrganization(organizationId);
      this.toast.success('Organization deleted successfully!');
      this.router.navigate(['/app/organizations']);
    } catch (error) {
      console.error('Failed to delete organization:', error);
      this.toast.error('Failed to delete organization. Please try again.');
    }
  }

  handleRetry(): void {
    const id = this.organizationId();
    if (id) {
      this.organizationService.fetchOrganization(id);
    }
  }

  handleAddMember(): void {
    const orgId = this.organizationId();
    if (!orgId) {
      return;
    }

    this.modal
      .open<{ added: boolean; error?: any }>(AddMemberModal, this.viewContainerRef, {
        size: 'md',
        data: {
          organizationId: orgId,
        },
      })
      .subscribe((result) => {
        if (result?.added) {
          // Members are automatically reloaded by the service
          this.toast.success('Member added successfully!');
        }
      });
  }

  handleChangeRole(member: OrganizationMember): void {
    const orgId = this.organizationId();
    if (!orgId) {
      return;
    }

    this.modal
      .open<{ changed: boolean; error?: any }>(ChangeRoleModal, this.viewContainerRef, {
        size: 'md',
        data: {
          organizationId: orgId,
          member: member,
        },
      })
      .subscribe((result) => {
        if (result?.changed) {
          // Members are automatically reloaded by the service
          this.toast.success('Member role updated successfully!');
        }
      });
  }

  async handleRemoveMember(member: OrganizationMember): Promise<void> {
    const orgId = this.organizationId();
    if (!orgId) {
      return;
    }

    // TODO: Add confirmation modal before removing
    try {
      await this.membersService.removeMember(orgId, member.user_id);
      this.toast.success(`Member "${member.user_name}" removed successfully.`);
      // Members are automatically reloaded by the service
    } catch (error: any) {
      console.error('Failed to remove member:', error);
      this.toast.error(error.message || 'Failed to remove member. Please try again.');
    }
  }

  handleMembersRetry(): void {
    const id = this.organizationId();
    if (id) {
      this.membersService.loadMembers(id);
    }
  }

  handleSendInvitation(): void {
    const orgId = this.organizationId();
    if (!orgId) {
      return;
    }

    this.modal
      .open<{ sent: boolean; error?: any }>(InviteMemberModal, this.viewContainerRef, {
        size: 'md',
        data: {
          organizationId: orgId,
        },
      })
      .subscribe((result) => {
        if (result?.sent) {
          // Invitations are automatically reloaded by the service
          this.toast.success('Invitation sent successfully!');
        }
      });
  }

  async handleCancelInvitation(invitation: OrganizationInvitation): Promise<void> {
    try {
      await this.invitationsService.cancelInvitation(invitation.id);
      this.toast.success(`Invitation to "${invitation.email}" canceled successfully.`);
      // Invitations are automatically reloaded by the service
    } catch (error: any) {
      console.error('Failed to cancel invitation:', error);
      const errorMessage =
        error?.error?.detail || error?.message || 'Failed to cancel invitation. Please try again.';
      this.toast.error(errorMessage);
    }
  }

  handleInvitationsRetry(): void {
    const id = this.organizationId();
    if (id) {
      this.invitationsService.loadInvitations(id);
    }
  }
}
