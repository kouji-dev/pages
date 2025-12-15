import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { Button, Input, ToastService } from 'shared-ui';
import { UserProfileService } from '../../application/services/user-profile.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-change-password-form',
  standalone: true,
  imports: [Button, Input, TranslatePipe],
  template: `
    <div class="change-password-form">
      <h2 class="change-password-form_title">{{ 'profile.changePassword.title' | translate }}</h2>
      <p class="change-password-form_description">
        {{ 'profile.changePassword.description' | translate }}
      </p>
      <form
        class="change-password-form_form"
        (ngSubmit)="handleSubmit()"
        (submit)="$event.preventDefault()"
      >
        <lib-input
          [label]="'profile.changePassword.currentPassword' | translate"
          type="password"
          [placeholder]="'profile.changePassword.currentPasswordPlaceholder' | translate"
          [(model)]="currentPassword"
          [required]="true"
          [errorMessage]="currentPasswordError()"
          [showPasswordToggle]="true"
          [helperText]="'profile.changePassword.currentPasswordHelper' | translate"
        />
        <lib-input
          [label]="'profile.changePassword.newPassword' | translate"
          type="password"
          [placeholder]="'profile.changePassword.newPasswordPlaceholder' | translate"
          [(model)]="newPassword"
          [required]="true"
          [errorMessage]="newPasswordError()"
          [showPasswordToggle]="true"
          [helperText]="passwordStrengthText()"
        />
        <lib-input
          [label]="'profile.changePassword.confirmPassword' | translate"
          type="password"
          [placeholder]="'profile.changePassword.confirmPasswordPlaceholder' | translate"
          [(model)]="confirmPassword"
          [required]="true"
          [errorMessage]="confirmPasswordError()"
          [showPasswordToggle]="true"
          [helperText]="'profile.changePassword.confirmPasswordHelper' | translate"
        />
        <div class="change-password-form_actions">
          <lib-button
            variant="primary"
            type="submit"
            [loading]="isSubmitting()"
            [disabled]="!isFormValid()"
          >
            {{ 'profile.changePassword.updatePassword' | translate }}
          </lib-button>
          <lib-button variant="secondary" (clicked)="handleReset()" [disabled]="isSubmitting()">
            {{ 'common.reset' | translate }}
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
        @apply text-text-primary;
        margin: 0;
      }

      .change-password-form_description {
        @apply text-sm;
        @apply text-text-secondary;
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
        @apply border-border-default;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChangePasswordForm {
  readonly userProfileService = inject(UserProfileService);
  readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);

  readonly currentPassword = signal('');
  readonly newPassword = signal('');
  readonly confirmPassword = signal('');
  readonly isSubmitting = signal(false);

  readonly currentPasswordError = computed(() => {
    const value = this.currentPassword();
    if (!value.trim()) {
      return this.translateService.instant('profile.changePassword.currentPasswordRequired');
    }
    return '';
  });

  readonly newPasswordError = computed(() => {
    const value = this.newPassword();
    if (!value.trim()) {
      return this.translateService.instant('profile.changePassword.newPasswordRequired');
    }
    if (value.length < 8) {
      return this.translateService.instant('auth.passwordMinLength');
    }
    if (!/[A-Z]/.test(value)) {
      return this.translateService.instant('auth.passwordUppercase');
    }
    if (!/[a-z]/.test(value)) {
      return this.translateService.instant('auth.passwordLowercase');
    }
    if (!/[0-9]/.test(value)) {
      return this.translateService.instant('auth.passwordNumber');
    }
    return '';
  });

  readonly confirmPasswordError = computed(() => {
    const value = this.confirmPassword();
    const newPasswordValue = this.newPassword();
    if (!value.trim()) {
      return this.translateService.instant('profile.changePassword.confirmPasswordRequired');
    }
    if (value !== newPasswordValue) {
      return this.translateService.instant('auth.passwordsDoNotMatch');
    }
    return '';
  });

  readonly passwordStrengthText = computed(() => {
    const value = this.newPassword();
    if (!value) {
      return this.translateService.instant('profile.changePassword.passwordRequirements');
    }
    if (this.newPasswordError()) {
      return this.newPasswordError();
    }
    return this.translateService.instant('profile.changePassword.passwordStrengthGood');
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
      this.toast.success(this.translateService.instant('profile.changePassword.updateSuccess'));
      this.handleReset();
    } catch (error) {
      console.error('Failed to update password:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('profile.changePassword.updateError');
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
