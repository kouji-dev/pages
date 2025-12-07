import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { Button, Input, ToastService } from 'shared-ui';
import { UserProfileService } from '../../application/services/user-profile.service';

@Component({
  selector: 'app-change-password-form',
  standalone: true,
  imports: [Button, Input],
  template: `
    <div class="change-password-form">
      <h2 class="change-password-form_title">Change Password</h2>
      <p class="change-password-form_description">
        Update your password to keep your account secure.
      </p>
      <form
        class="change-password-form_form"
        (ngSubmit)="handleSubmit()"
        (submit)="$event.preventDefault()"
      >
        <lib-input
          label="Current Password"
          type="password"
          placeholder="Enter your current password"
          [(model)]="currentPassword"
          [required]="true"
          [errorMessage]="currentPasswordError()"
          [showPasswordToggle]="true"
          helperText="Enter your current password to verify your identity"
        />
        <lib-input
          label="New Password"
          type="password"
          placeholder="Enter your new password"
          [(model)]="newPassword"
          [required]="true"
          [errorMessage]="newPasswordError()"
          [showPasswordToggle]="true"
          [helperText]="passwordStrengthText()"
        />
        <lib-input
          label="Confirm New Password"
          type="password"
          placeholder="Confirm your new password"
          [(model)]="confirmPassword"
          [required]="true"
          [errorMessage]="confirmPasswordError()"
          [showPasswordToggle]="true"
          helperText="Re-enter your new password to confirm"
        />
        <div class="change-password-form_actions">
          <lib-button
            variant="primary"
            type="submit"
            [loading]="isSubmitting()"
            [disabled]="!isFormValid()"
          >
            Update Password
          </lib-button>
          <lib-button variant="secondary" (clicked)="handleReset()" [disabled]="isSubmitting()">
            Reset
          </lib-button>
        </div>
      </form>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .change-password-form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .change-password-form_title {
        @apply text-xl font-semibold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .change-password-form_description {
        @apply text-sm;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .change-password-form_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .change-password-form_actions {
        @apply flex items-center;
        @apply gap-3;
        @apply pt-4;
        @apply border-t;
        border-color: var(--color-border-default);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChangePasswordForm {
  readonly userProfileService = inject(UserProfileService);
  readonly toast = inject(ToastService);

  readonly currentPassword = signal('');
  readonly newPassword = signal('');
  readonly confirmPassword = signal('');
  readonly isSubmitting = signal(false);

  readonly currentPasswordError = computed(() => {
    const value = this.currentPassword();
    if (!value.trim()) {
      return 'Current password is required';
    }
    return '';
  });

  readonly newPasswordError = computed(() => {
    const value = this.newPassword();
    if (!value.trim()) {
      return 'New password is required';
    }
    if (value.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    if (!/[A-Z]/.test(value)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/[a-z]/.test(value)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/[0-9]/.test(value)) {
      return 'Password must contain at least one number';
    }
    return '';
  });

  readonly confirmPasswordError = computed(() => {
    const value = this.confirmPassword();
    const newPasswordValue = this.newPassword();
    if (!value.trim()) {
      return 'Please confirm your new password';
    }
    if (value !== newPasswordValue) {
      return 'Passwords do not match';
    }
    return '';
  });

  readonly passwordStrengthText = computed(() => {
    const value = this.newPassword();
    if (!value) {
      return 'Password must be at least 8 characters with uppercase, lowercase, and number';
    }
    if (this.newPasswordError()) {
      return this.newPasswordError();
    }
    return 'Password strength: Good';
  });

  readonly isFormValid = computed(() => {
    return (
      !this.currentPasswordError() &&
      !this.newPasswordError() &&
      !this.confirmPasswordError() &&
      this.currentPassword().trim().length > 0 &&
      this.newPassword().trim().length > 0 &&
      this.confirmPassword().trim().length > 0
    );
  });

  async handleSubmit(): Promise<void> {
    if (!this.isFormValid()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      await this.userProfileService.updatePassword({
        current_password: this.currentPassword(),
        new_password: this.newPassword(),
      });
      this.toast.success('Password updated successfully!');
      this.handleReset();
    } catch (error) {
      console.error('Failed to update password:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update password. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }

  handleReset(): void {
    this.currentPassword.set('');
    this.newPassword.set('');
    this.confirmPassword.set('');
  }
}
