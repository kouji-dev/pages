import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  ViewContainerRef,
  effect,
} from '@angular/core';
import { Button, Input, LoadingState, ErrorState, Modal } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { OrganizationService, Organization } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { DeleteOrganizationModal } from '../components/delete-organization-modal';
import { MemberList } from '../components/member-list';
import { AddMemberModal } from '../components/add-member-modal';
import { ChangeRoleModal } from '../components/change-role-modal';
import { PendingInvitations } from '../components/pending-invitations';
import { InviteMemberModal } from '../components/invite-member-modal';
import { BackToPage } from '../components/back-to-page';
import {
  OrganizationMembersService,
  OrganizationMember,
} from '../../application/services/organization-members.service';
import {
  OrganizationInvitationsService,
  OrganizationInvitation,
} from '../../application/services/organization-invitations.service';
import { AuthService } from '../../application/services/auth.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-organization-settings-page',
  imports: [
    Button,
    Input,
    LoadingState,
    ErrorState,
    MemberList,
    PendingInvitations,
    BackToPage,
    TranslatePipe,
  ],
  template: `
    <div class="org-settings-page">
      <div class="org-settings-page_header">
        <div class="org-settings-page_header-content">
          <div>
            <app-back-to-page
              [label]="'organizations.backToOrganizations' | translate"
              [route]="['/app/organizations']"
            />
            <h1 class="org-settings-page_title">
              {{ 'organizations.settings.title' | translate }}
            </h1>
            @if (organization()) {
              <p class="org-settings-page_subtitle">{{ organization()!.name }}</p>
            }
          </div>
        </div>
      </div>

      <div class="org-settings-page_content">
        @if (isLoading()) {
          <lib-loading-state [message]="'organizations.loadingOrganization' | translate" />
        } @else if (error()) {
          <lib-error-state
            [title]="'organizations.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else if (!organization()) {
          <lib-error-state
            [title]="'organizations.notFound' | translate"
            [message]="'organizations.notFoundDescription' | translate"
            [showRetry]="false"
          />
        } @else {
          <div class="org-settings-page_container">
            <!-- Organization Details Form -->
            <div class="org-settings-page_section">
              <h2 class="org-settings-page_section-title">
                {{ 'organizations.settings.details' | translate }}
              </h2>
              <form class="org-settings-page_form" (ngSubmit)="handleSave()">
                <lib-input
                  [label]="'organizations.settings.name' | translate"
                  [placeholder]="'organizations.settings.namePlaceholder' | translate"
                  [(model)]="name"
                  [required]="true"
                  [errorMessage]="nameError()"
                  [helperText]="'organizations.settings.nameHelper' | translate"
                />
                <lib-input
                  [label]="'organizations.settings.description' | translate"
                  type="textarea"
                  [placeholder]="'organizations.settings.descriptionPlaceholder' | translate"
                  [(model)]="description"
                  [rows]="4"
                  [helperText]="'organizations.settings.descriptionHelper' | translate"
                />
                <div class="org-settings-page_form-actions">
                  <lib-button
                    variant="primary"
                    type="submit"
                    [loading]="isSaving()"
                    [disabled]="!isFormValid() || !hasChanges()"
                  >
                    {{ 'common.saveChanges' | translate }}
                  </lib-button>
                  <lib-button
                    variant="secondary"
                    (clicked)="handleReset()"
                    [disabled]="!hasChanges() || isSaving()"
                  >
                    {{ 'common.cancel' | translate }}
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
              <h2 class="org-settings-page_section-title">
                {{ 'organizations.settings.dangerZone' | translate }}
              </h2>
              <div class="org-settings-page_danger-content">
                <div>
                  <h3 class="org-settings-page_danger-title">
                    {{ 'organizations.settings.deleteTitle' | translate }}
                  </h3>
                  <p class="org-settings-page_danger-description">
                    {{ 'organizations.settings.deleteDescription' | translate }}
                  </p>
                </div>
                <lib-button
                  variant="danger"
                  (clicked)="handleDeleteClick()"
                  [disabled]="isDeleting()"
                >
                  {{ 'organizations.deleteOrganization' | translate }}
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
  private readonly organizationService = inject(OrganizationService);
  private readonly navigationService = inject(NavigationService);
  readonly membersService = inject(OrganizationMembersService);
  readonly invitationsService = inject(OrganizationInvitationsService);
  private readonly authService = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  readonly name = signal('');
  readonly description = signal('');
  readonly isSaving = signal(false);
  readonly isDeleting = signal(false);

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId();
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
      return this.translateService.instant('organizations.settings.nameRequired');
    }
    if (value.trim().length < 3) {
      return this.translateService.instant('organizations.settings.nameMinLength');
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
        : this.translateService.instant('organizations.loadError');
    }
    return this.translateService.instant('common.unknownError');
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
  private readonly loadMembersEffect = effect(() => {
    const id = this.organizationId();
    if (id) {
      // Organization is automatically loaded from URL via organizationResource
      // Just load members when organization ID is available
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
        this.toast.success(this.translateService.instant('organizations.updateSuccess'));
        // Reload organization to get updated data
        this.organizationService.reloadCurrentOrganization();
      })
      .catch((error) => {
        console.error('Failed to update organization:', error);
        this.toast.error(this.translateService.instant('organizations.updateError'));
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
      this.toast.success(this.translateService.instant('organizations.deleteSuccess'));
      this.navigationService.navigateToOrganizations();
    } catch (error) {
      console.error('Failed to delete organization:', error);
      this.toast.error(this.translateService.instant('organizations.deleteError'));
    }
  }

  handleRetry(): void {
    // Reload current organization resource
    this.organizationService.reloadCurrentOrganization();
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
          this.toast.success(this.translateService.instant('members.addMemberSuccess'));
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
          this.toast.success(this.translateService.instant('members.updateRoleSuccess'));
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
      this.toast.success(
        this.translateService.instant('members.removeSuccess', { userName: member.user_name }),
      );
      // Members are automatically reloaded by the service
    } catch (error: any) {
      console.error('Failed to remove member:', error);
      this.toast.error(error.message || this.translateService.instant('members.removeError'));
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
          this.toast.success(this.translateService.instant('invitations.invitationSent'));
        }
      });
  }

  async handleCancelInvitation(invitation: OrganizationInvitation): Promise<void> {
    try {
      await this.invitationsService.cancelInvitation(invitation.id);
      this.toast.success(
        this.translateService.instant('invitations.cancelSuccess', { email: invitation.email }),
      );
      // Invitations are automatically reloaded by the service
    } catch (error: any) {
      console.error('Failed to cancel invitation:', error);
      const errorMessage =
        error?.error?.detail ||
        error?.message ||
        this.translateService.instant('invitations.cancelError');
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
