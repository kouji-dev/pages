import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Button, Input, ToastService } from 'shared-ui';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../../application/services/auth.service';

@Component({
  selector: 'app-forgot-password-page',
  standalone: true,
  imports: [Button, Input, RouterLink],
  template: `
    <div class="forgot-password-page">
      <div class="forgot-password-page_container">
        <div class="forgot-password-page_content">
          <h1 class="forgot-password-page_title">Forgot Password?</h1>
          <p class="forgot-password-page_subtitle">
            Enter your email address and we'll send you a link to reset your password.
          </p>

          <form
            class="forgot-password-page_form"
            (ngSubmit)="handleSubmit()"
            (submit)="$event.preventDefault()"
          >
            <lib-input
              label="Email"
              type="email"
              placeholder="Enter your email"
              [(model)]="email"
              [required]="true"
              [errorMessage]="emailError()"
              helperText="Enter the email address associated with your account"
            />

            <div class="forgot-password-page_actions">
              <lib-button
                variant="primary"
                type="submit"
                [loading]="isSubmitting()"
                [disabled]="!isFormValid()"
                class="forgot-password-page_submit-button"
              >
                Send Reset Link
              </lib-button>
            </div>
          </form>

          @if (isSuccess()) {
            <div class="forgot-password-page_success">
              <p class="forgot-password-page_success-text">
                If an account exists with this email, we've sent a password reset link. Please check
                your inbox.
              </p>
            </div>
          }

          <div class="forgot-password-page_footer">
            <a routerLink="/login" class="forgot-password-page_link">Back to Sign In</a>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .forgot-password-page {
        @apply min-h-screen;
        @apply flex items-center justify-center;
        @apply px-4;
        @apply py-12;
        @apply bg-bg-primary;
      }

      .forgot-password-page_container {
        @apply w-full;
        @apply max-w-md;
      }

      .forgot-password-page_content {
        @apply flex flex-col;
        @apply gap-8;
        @apply p-8;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .forgot-password-page_title {
        @apply text-3xl font-bold;
        @apply mb-2;
        @apply text-text-primary;
        margin: 0;
      }

      .forgot-password-page_subtitle {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .forgot-password-page_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .forgot-password-page_actions {
        @apply flex flex-col;
        @apply gap-3;
        @apply pt-2;
      }

      .forgot-password-page_submit-button {
        @apply w-full;
      }

      .forgot-password-page_success {
        @apply p-4;
        @apply rounded-md;
        @apply border;
        @apply border-success-200;
        @apply bg-success-50;
      }

      .forgot-password-page_success-text {
        @apply text-sm;
        @apply text-success-700;
        margin: 0;
      }

      .forgot-password-page_footer {
        @apply text-center;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .forgot-password-page_link {
        @apply text-sm;
        @apply font-medium;
        @apply text-primary-600;
        text-decoration: none;
      }

      .forgot-password-page_link:hover {
        @apply text-primary-700;
        text-decoration: underline;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ForgotPasswordPage {
  private readonly authService = inject(AuthService);
  private readonly toast = inject(ToastService);

  readonly email = signal('');
  readonly isSubmitting = signal(false);
  readonly isSuccess = signal(false);

  readonly emailError = computed(() => {
    const value = this.email();
    if (!value.trim()) {
      return 'Email is required';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value.trim())) {
      return 'Please enter a valid email address';
    }
    return '';
  });

  readonly isFormValid = computed(() => {
    return !this.emailError() && this.email().trim().length > 0;
  });

  async handleSubmit(): Promise<void> {
    if (!this.isFormValid()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      await firstValueFrom(this.authService.requestPasswordReset(this.email().trim()));
      this.isSuccess.set(true);
      this.toast.success('Password reset link sent! Please check your email.');
    } catch (error) {
      // Error is already handled by error interceptor
      console.error('Password reset request failed:', error);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
