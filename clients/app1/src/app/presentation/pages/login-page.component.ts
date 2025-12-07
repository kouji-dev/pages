import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { Button, Input, ToastService } from 'shared-ui';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../../application/services/auth.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [Button, Input, RouterLink],
  template: `
    <div class="login-page">
      <div class="login-page_container">
        <div class="login-page_content">
          <h1 class="login-page_title">Welcome back</h1>
          <p class="login-page_subtitle">Sign in to your account to continue</p>

          <form
            class="login-page_form"
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
              helperText="Enter your registered email address"
            />

            <lib-input
              label="Password"
              type="password"
              placeholder="Enter your password"
              [(model)]="password"
              [required]="true"
              [errorMessage]="passwordError()"
              [showPasswordToggle]="true"
            />

            <div class="login-page_actions">
              <lib-button
                variant="primary"
                type="submit"
                [loading]="isSubmitting()"
                [disabled]="!isFormValid()"
                class="login-page_submit-button"
                (clicked)="handleSubmit()"
              >
                Sign In
              </lib-button>
            </div>
          </form>

          <div class="login-page_footer">
            <p class="login-page_footer-text">
              Don't have an account?
              <a routerLink="/register" class="login-page_link">Sign up</a>
            </p>
            <a routerLink="/forgot-password" class="login-page_forgot-link">Forgot password?</a>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .login-page {
        @apply min-h-screen;
        @apply flex items-center justify-center;
        @apply px-4;
        @apply py-12;
        @apply bg-bg-primary;
      }

      .login-page_container {
        @apply w-full;
        @apply max-w-md;
      }

      .login-page_content {
        @apply flex flex-col;
        @apply gap-8;
        @apply p-8;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .login-page_title {
        @apply text-3xl font-bold;
        @apply mb-2;
        @apply text-text-primary;
        margin: 0;
      }

      .login-page_subtitle {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .login-page_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .login-page_actions {
        @apply flex flex-col;
        @apply gap-3;
        @apply pt-2;
      }

      .login-page_submit-button {
        @apply w-full;
      }

      .login-page_footer {
        @apply flex flex-col;
        @apply gap-2;
        @apply text-center;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .login-page_footer-text {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .login-page_link {
        @apply font-medium;
        @apply text-primary-600;
        text-decoration: none;
      }

      .login-page_link:hover {
        @apply text-primary-700;
        text-decoration: underline;
      }

      .login-page_forgot-link {
        @apply text-sm;
        @apply font-medium;
        @apply text-primary-600;
        text-decoration: none;
      }

      .login-page_forgot-link:hover {
        @apply text-primary-700;
        text-decoration: underline;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginPage {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  readonly email = signal('');
  readonly password = signal('');
  readonly isSubmitting = signal(false);

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

  readonly passwordError = computed(() => {
    const value = this.password();
    if (!value.trim()) {
      return 'Password is required';
    }
    return '';
  });

  readonly isFormValid = computed(() => {
    return (
      !this.emailError() &&
      !this.passwordError() &&
      this.email().trim().length > 0 &&
      this.password().trim().length > 0
    );
  });

  async handleSubmit(): Promise<void> {
    if (!this.isFormValid() || this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      await firstValueFrom(
        this.authService.login({
          email: this.email().trim(),
          password: this.password(),
        }),
      );

      this.toast.success('Welcome back!');
      this.router.navigate(['/app']);
    } catch (error) {
      // Error is already handled by error interceptor
      console.error('Login failed:', error);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
