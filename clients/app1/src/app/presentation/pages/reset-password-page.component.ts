import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { Button, Input, ToastService } from 'shared-ui';
import { firstValueFrom } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { AuthService } from '../../application/services/auth.service';

@Component({
  selector: 'app-reset-password-page',
  standalone: true,
  imports: [Button, Input, RouterLink],
  template: `
    <div class="reset-password-page">
      <div class="reset-password-page_container">
        <div class="reset-password-page_content">
          <h1 class="reset-password-page_title">Reset Password</h1>
          <p class="reset-password-page_subtitle">Enter your new password below</p>

          @if (isInvalidToken()) {
            <div class="reset-password-page_error">
              <p class="reset-password-page_error-text">
                Invalid or expired reset token. Please request a new password reset link.
              </p>
              <lib-button variant="primary" [link]="'/forgot-password'">
                Request New Link
              </lib-button>
            </div>
          } @else {
            <form
              class="reset-password-page_form"
              (ngSubmit)="handleSubmit()"
              (submit)="$event.preventDefault()"
            >
              <lib-input
                label="New Password"
                type="password"
                placeholder="Enter your new password"
                [(model)]="password"
                [required]="true"
                [errorMessage]="passwordError()"
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
              />

              <div class="reset-password-page_actions">
                <lib-button
                  variant="primary"
                  type="submit"
                  [loading]="isSubmitting()"
                  [disabled]="!isFormValid()"
                  class="reset-password-page_submit-button"
                >
                  Reset Password
                </lib-button>
              </div>
            </form>
          }

          @if (isSuccess()) {
            <div class="reset-password-page_success">
              <p class="reset-password-page_success-text">
                Your password has been reset successfully. You can now sign in with your new
                password.
              </p>
              <lib-button variant="primary" [link]="'/login'">Go to Sign In</lib-button>
            </div>
          }

          <div class="reset-password-page_footer">
            <a routerLink="/login" class="reset-password-page_link">Back to Sign In</a>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .reset-password-page {
        @apply min-h-screen;
        @apply flex items-center justify-center;
        @apply px-4;
        @apply py-12;
        @apply bg-bg-primary;
      }

      .reset-password-page_container {
        @apply w-full;
        @apply max-w-md;
      }

      .reset-password-page_content {
        @apply flex flex-col;
        @apply gap-8;
        @apply p-8;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .reset-password-page_title {
        @apply text-3xl font-bold;
        @apply mb-2;
        @apply text-text-primary;
        margin: 0;
      }

      .reset-password-page_subtitle {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .reset-password-page_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .reset-password-page_actions {
        @apply flex flex-col;
        @apply gap-3;
        @apply pt-2;
      }

      .reset-password-page_submit-button {
        @apply w-full;
      }

      .reset-password-page_error {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-4;
        @apply rounded-md;
        @apply border;
        @apply border-error-200;
        @apply bg-error-50;
      }

      .reset-password-page_error-text {
        @apply text-sm;
        @apply text-error-700;
        margin: 0;
      }

      .reset-password-page_success {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-4;
        @apply rounded-md;
        @apply border;
        @apply border-success-200;
        @apply bg-success-50;
      }

      .reset-password-page_success-text {
        @apply text-sm;
        @apply text-success-700;
        margin: 0;
      }

      .reset-password-page_footer {
        @apply text-center;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .reset-password-page_link {
        @apply text-sm;
        @apply font-medium;
        @apply text-primary-600;
        text-decoration: none;
      }

      .reset-password-page_link:hover {
        @apply text-primary-700;
        text-decoration: underline;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResetPasswordPage {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly toast = inject(ToastService);

  readonly password = signal('');
  readonly confirmPassword = signal('');
  readonly isSubmitting = signal(false);
  readonly isSuccess = signal(false);
  readonly hasTokenError = signal(false);

  // Get token from route query params
  private readonly routeParams = toSignal(
    this.route.queryParams.pipe(map((params) => params['token'] as string | undefined)),
    { initialValue: undefined },
  );

  readonly resetToken = computed(() => this.routeParams() || null);
  readonly isInvalidToken = computed(() => !this.resetToken() || this.hasTokenError());

  readonly passwordError = computed(() => {
    const value = this.password();
    if (!value.trim()) {
      return 'Password is required';
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
    const passwordValue = this.password();
    if (!value.trim()) {
      return 'Please confirm your password';
    }
    if (value !== passwordValue) {
      return 'Passwords do not match';
    }
    return '';
  });

  readonly passwordStrengthText = computed(() => {
    const value = this.password();
    if (!value) {
      return 'Password must be at least 8 characters with uppercase, lowercase, and number';
    }
    if (this.passwordError()) {
      return this.passwordError();
    }
    // Calculate strength
    let strength = 0;
    if (value.length >= 8) strength++;
    if (/[A-Z]/.test(value)) strength++;
    if (/[a-z]/.test(value)) strength++;
    if (/[0-9]/.test(value)) strength++;
    if (/[^A-Za-z0-9]/.test(value)) strength++;

    if (strength <= 2) {
      return 'Password strength: Weak';
    } else if (strength <= 4) {
      return 'Password strength: Medium';
    } else {
      return 'Password strength: Strong';
    }
  });

  readonly isFormValid = computed(() => {
    return (
      !this.passwordError() &&
      !this.confirmPasswordError() &&
      this.password().trim().length > 0 &&
      this.confirmPassword().trim().length > 0 &&
      !!this.resetToken()
    );
  });

  async handleSubmit(): Promise<void> {
    if (!this.isFormValid() || !this.resetToken()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      await firstValueFrom(this.authService.resetPassword(this.resetToken()!, this.password()));

      this.isSuccess.set(true);
      this.toast.success('Password reset successfully!');
    } catch (error) {
      // Check if it's a token error
      if (error && typeof error === 'object' && 'status' in error && error.status === 400) {
        this.hasTokenError.set(true);
      }
      // Error is already handled by error interceptor
      console.error('Password reset failed:', error);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
