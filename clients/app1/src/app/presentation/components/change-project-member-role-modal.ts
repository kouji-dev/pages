import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  effect,
  input,
} from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter, Button } from 'shared-ui';
import { ToastService } from 'shared-ui';
import {
  ProjectMembersService,
  ProjectMember,
  UpdateProjectMemberRoleRequest,
} from '../../application/services/project-members.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-change-project-member-role-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{ 'members.changeRole' | translate }}</lib-modal-header>
      <lib-modal-content>
        <div class="change-project-role-form">
          <div class="change-project-role-form_info">
            <div class="change-project-role-form_member">
              <div class="change-project-role-form_member-avatar">
                @if (member().avatar_url) {
                  <img
                    [src]="member().avatar_url"
                    [alt]="member().user_name"
                    class="change-project-role-form_member-avatar-image"
                  />
                } @else {
                  <div class="change-project-role-form_member-avatar-placeholder">
                    {{ getInitials(member().user_name) }}
                  </div>
                }
              </div>
              <div class="change-project-role-form_member-info">
                <div class="change-project-role-form_member-name">{{ member().user_name }}</div>
                <div class="change-project-role-form_member-email">
                  {{ member().user_email }}
                </div>
              </div>
            </div>
            <div class="change-project-role-form_current-role">
              <span class="change-project-role-form_current-role-label"
                >{{ 'members.currentRole' | translate }}:</span
              >
              <span
                class="change-project-role-form_role-badge"
                [class]="'change-project-role-form_role-badge--' + member().role"
              >
                {{ getRoleLabel(member().role) }}
              </span>
            </div>
          </div>

          <div class="change-project-role-form_role">
            <label class="change-project-role-form_role-label">{{
              'members.newRole' | translate
            }}</label>
            <div class="change-project-role-form_role-options">
              @for (role of availableRoles(); track role.value) {
                <button
                  type="button"
                  class="change-project-role-form_role-option"
                  [class.change-project-role-form_role-option--selected]="
                    selectedRole() === role.value
                  "
                  [class.change-project-role-form_role-option--disabled]="
                    role.value === member().role
                  "
                  (click)="selectRole(role.value)"
                >
                  <div class="change-project-role-form_role-option-header">
                    <span class="change-project-role-form_role-option-name">{{ role.label }}</span>
                    @if (role.value === member().role) {
                      <span class="change-project-role-form_role-option-current">{{
                        'members.current' | translate
                      }}</span>
                    }
                  </div>
                  <p class="change-project-role-form_role-option-description">
                    {{ role.description }}
                  </p>
                </button>
              }
            </div>
          </div>
        </div>
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
          {{ 'common.saveChanges' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .change-project-role-form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .change-project-role-form_info {
        @apply flex flex-col;
        @apply gap-4;
        @apply pb-4;
        @apply border-b;
        @apply border-border-default;
      }

      .change-project-role-form_member {
        @apply flex items-center;
        @apply gap-3;
      }

      .change-project-role-form_member-avatar {
        @apply w-12 h-12;
        @apply rounded-full;
        @apply overflow-hidden;
        @apply flex-shrink-0;
        @apply bg-bg-tertiary;
      }

      .change-project-role-form_member-avatar-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .change-project-role-form_member-avatar-placeholder {
        @apply w-full h-full;
        @apply flex items-center justify-center;
        @apply text-sm font-semibold;
        @apply text-text-primary;
      }

      .change-project-role-form_member-info {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-w-0;
      }

      .change-project-role-form_member-name {
        @apply text-sm font-medium;
        @apply text-text-primary;
        @apply truncate;
      }

      .change-project-role-form_member-email {
        @apply text-xs;
        @apply text-text-secondary;
        @apply truncate;
      }

      .change-project-role-form_current-role {
        @apply flex items-center gap-2;
      }

      .change-project-role-form_current-role-label {
        @apply text-sm;
        @apply text-text-secondary;
      }

      .change-project-role-form_role-badge {
        @apply inline-flex items-center;
        @apply px-2.5 py-1;
        @apply rounded-full;
        @apply text-xs font-medium;
      }

      .change-project-role-form_role-badge--admin {
        @apply bg-primary-100;
        @apply text-primary-700;
      }

      .change-project-role-form_role-badge--member {
        @apply bg-gray-100;
        @apply text-gray-700;
      }

      .change-project-role-form_role-badge--viewer {
        @apply bg-gray-50;
        @apply text-gray-600;
      }

      .change-project-role-form_role {
        @apply flex flex-col;
        @apply gap-3;
      }

      .change-project-role-form_role-label {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .change-project-role-form_role-options {
        @apply grid grid-cols-1 gap-2;
      }

      .change-project-role-form_role-option {
        @apply flex flex-col;
        @apply gap-1;
        @apply p-3;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
        @apply transition-colors;
        @apply cursor-pointer;
        @apply hover:bg-bg-hover;
        text-align: left;
      }

      .change-project-role-form_role-option--selected {
        @apply border-primary-500;
        @apply bg-primary-50;
      }

      .change-project-role-form_role-option--disabled {
        opacity: 0.6;
        @apply cursor-not-allowed;
      }

      .change-project-role-form_role-option-header {
        @apply flex items-center justify-between;
      }

      .change-project-role-form_role-option-name {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .change-project-role-form_role-option-current {
        @apply text-xs;
        @apply px-2 py-0.5;
        @apply rounded;
        @apply bg-gray-200;
        @apply text-gray-700;
      }

      .change-project-role-form_role-option-description {
        @apply text-xs;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChangeProjectMemberRoleModal {
  private readonly modal = inject(Modal);
  private readonly membersService = inject(ProjectMembersService);
  private readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);

  readonly projectId = input.required<string>();
  readonly member = input.required<ProjectMember>();
  readonly selectedRole = signal<'admin' | 'member' | 'viewer'>('member');
  readonly isSubmitting = signal(false);

  private readonly syncSelectedRoleEffect = effect(
    () => {
      const member = this.member();
      if (member) {
        this.selectedRole.set(member.role);
      }
    },
    { allowSignalWrites: true },
  );

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

  readonly isValid = computed(() => {
    return this.selectedRole() !== this.member().role && !this.isSubmitting();
  });

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

  selectRole(role: 'admin' | 'member' | 'viewer'): void {
    if (role === this.member().role) {
      return; // Don't allow selecting current role
    }
    this.selectedRole.set(role);
  }

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      const request: UpdateProjectMemberRoleRequest = {
        role: this.selectedRole(),
      };

      await this.membersService.updateMemberRole(this.projectId(), this.member().user_id, request);
      this.toast.success(this.translateService.instant('members.updateRoleSuccess'));
      this.modal.close({ success: true });
    } catch (error) {
      console.error('Failed to update member role:', error);
      this.toast.error(this.translateService.instant('members.updateRoleError'));
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
