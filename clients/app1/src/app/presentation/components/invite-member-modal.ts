import { Component, ChangeDetectionStrategy, signal, computed, inject, input } from '@angular/core';
import {
  Modal,
  ModalContainer,
  ModalHeader,
  ModalContent,
  ModalFooter,
  Button,
  Input,
} from 'shared-ui';
import { ToastService } from 'shared-ui';
import {
  OrganizationInvitationsService,
  SendInvitationRequest,
} from '../../application/services/organization-invitations.service';

@Component({
  selector: 'app-invite-member-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input],
  template: `
    <lib-modal-container>
      <lib-modal-header>Send Invitation</lib-modal-header>
      <lib-modal-content>
        <form class="invite-member-form" (ngSubmit)="handleSubmit()">
          <lib-input
            label="Email Address"
            type="email"
            placeholder="Enter email address..."
            [(model)]="email"
            [required]="true"
            [errorMessage]="emailError()"
            helperText="The email address of the person you want to invite"
          />

          <div class="invite-member-form_role">
            <label class="invite-member-form_role-label">Role</label>
            <div class="invite-member-form_role-options">
              @for (role of availableRoles(); track role.value) {
                <button
                  type="button"
                  class="invite-member-form_role-option"
                  [class.invite-member-form_role-option--selected]="selectedRole() === role.value"
                  (click)="selectedRole.set(role.value)"
                >
                  <div class="invite-member-form_role-option-header">
                    <span class="invite-member-form_role-option-name">{{ role.label }}</span>
                  </div>
                  <p class="invite-member-form_role-option-description">{{ role.description }}</p>
                </button>
              }
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
          Send Invitation
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .invite-member-form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .invite-member-form_role {
        @apply flex flex-col;
        @apply gap-3;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .invite-member-form_role-label {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .invite-member-form_role-options {
        @apply grid grid-cols-1 gap-2;
      }

      .invite-member-form_role-option {
        @apply flex flex-col;
        @apply gap-1;
        @apply p-3;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
        @apply transition-colors;
        @apply cursor-pointer;
        @apply hover:bg-gray-50;
        text-align: left;
      }

      .invite-member-form_role-option--selected {
        @apply border-primary-500;
        @apply bg-primary-50;
      }

      .invite-member-form_role-option-header {
        @apply flex items-center justify-between;
      }

      .invite-member-form_role-option-name {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .invite-member-form_role-option-description {
        @apply text-xs;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InviteMemberModal {
  private readonly modal = inject(Modal);
  private readonly invitationsService = inject(OrganizationInvitationsService);
  private readonly toast = inject(ToastService);

  readonly organizationId = input.required<string>();
  readonly email = signal('');
  readonly selectedRole = signal<'admin' | 'member' | 'viewer'>('member');
  readonly isSubmitting = signal(false);

  readonly availableRoles = computed(() => [
    {
      value: 'admin' as const,
      label: 'Admin',
      description: 'Full access to manage organization and members',
    },
    {
      value: 'member' as const,
      label: 'Member',
      description: 'Can create and edit projects, but cannot manage members',
    },
    {
      value: 'viewer' as const,
      label: 'Viewer',
      description: 'Read-only access to organization content',
    },
  ]);

  readonly emailError = computed(() => {
    const value = this.email().trim();
    if (!value) {
      return 'Email address is required';
    }
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return 'Please enter a valid email address';
    }
    return '';
  });

  readonly isValid = computed(() => {
    return !this.emailError() && this.email().trim().length > 0 && !this.isSubmitting();
  });

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    const emailValue = this.email().trim();
    if (!emailValue) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      const request: SendInvitationRequest = {
        email: emailValue,
        role: this.selectedRole(),
      };

      await this.invitationsService.sendInvitation(this.organizationId()!, request);
      this.toast.success('Invitation sent successfully!');
      this.modal.close({ sent: true });
    } catch (error: any) {
      console.error('Failed to send invitation:', error);
      const errorMessage =
        error?.error?.detail || error?.message || 'Failed to send invitation. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
