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
} from '../../../../application/services/organization-invitations.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-invite-member-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{ 'invitations.title' | translate }}</lib-modal-header>
      <lib-modal-content>
        <form class="invite-member-form" (ngSubmit)="handleSubmit()">
          <lib-input
            [label]="'invitations.emailLabel' | translate"
            type="email"
            [placeholder]="'invitations.emailPlaceholder' | translate"
            [(model)]="email"
            [required]="true"
            [errorMessage]="emailError()"
            [helperText]="'invitations.emailHelper' | translate"
          />

          <div class="invite-member-form_role">
            <label class="invite-member-form_role-label">{{ 'members.role' | translate }}</label>
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
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button
          variant="primary"
          (clicked)="handleSubmit()"
          [loading]="isSubmitting()"
          [disabled]="!isValid()"
        >
          {{ 'invitations.sendInvitation' | translate }}
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
        @apply border-border;
      }

      .invite-member-form_role-label {
        @apply text-sm font-medium;
        @apply text-foreground;
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
        @apply border-border;
        @apply bg-background;
        @apply transition-colors;
        @apply cursor-pointer;
        @apply hover:bg-muted;
        text-align: left;
      }

      .invite-member-form_role-option--selected {
        @apply border-primary;
        @apply bg-primary/10;
      }

      .invite-member-form_role-option-header {
        @apply flex items-center justify-between;
      }

      .invite-member-form_role-option-name {
        @apply text-sm font-medium;
        @apply text-foreground;
      }

      .invite-member-form_role-option-description {
        @apply text-xs;
        @apply text-muted-foreground;
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
  private readonly translateService = inject(TranslateService);

  readonly organizationId = input.required<string>();
  readonly email = signal('');
  readonly selectedRole = signal<'admin' | 'member' | 'viewer'>('member');
  readonly isSubmitting = signal(false);

  readonly availableRoles = computed(() => [
    {
      value: 'admin' as const,
      label: this.translateService.instant('members.admin'),
      description: this.translateService.instant('members.adminDescription'),
    },
    {
      value: 'member' as const,
      label: this.translateService.instant('members.member'),
      description: this.translateService.instant('members.memberDescription'),
    },
    {
      value: 'viewer' as const,
      label: this.translateService.instant('members.viewer'),
      description: this.translateService.instant('members.viewerDescription'),
    },
  ]);

  readonly emailError = computed(() => {
    const value = this.email().trim();
    if (!value) {
      return this.translateService.instant('invitations.emailRequired');
    }
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return this.translateService.instant('invitations.emailInvalid');
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
      this.toast.success(this.translateService.instant('invitations.invitationSent'));
      this.modal.close({ sent: true });
    } catch (error: any) {
      console.error('Failed to send invitation:', error);
      const errorMessage =
        error?.error?.detail ||
        error?.message ||
        this.translateService.instant('invitations.invitationError');
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
