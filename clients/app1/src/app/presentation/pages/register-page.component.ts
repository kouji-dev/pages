import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { Button, Input, ToastService } from 'shared-ui';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../../application/services/auth.service';

@Component({
  selector: 'app-register-page',
  standalone: true,
  imports: [Button, Input, RouterLink],
  template: `
    <div class="register-page">
      <div class="register-page_container">
        <div class="register-page_content">
          <h1 class="register-page_title">Create an account</h1>
          <p class="register-page_subtitle">Sign up to get started with Pages</p>

          <form
            class="register-page_form"
            (ngSubmit)="handleSubmit()"
            (submit)="$event.preventDefault()"
          >
            <lib-input
              label="Name"
              type="text"
              placeholder="Enter your full name"
              [(model)]="name"
              [required]="true"
              [errorMessage]="nameError()"
              helperText="This will be displayed on your profile"
            />

            <lib-input
              label="Email"
              type="email"
              placeholder="Enter your email"
              [(model)]="email"
              [required]="true"
              [errorMessage]="emailError()"
              helperText="We'll never share your email"
            />

            <lib-input
              label="Password"
              type="password"
              placeholder="Create a password"
              [(model)]="password"
              [required]="true"
              [errorMessage]="passwordError()"
              [showPasswordToggle]="true"
              [helperText]="passwordStrengthText()"
            />

            <lib-input
              label="Confirm Password"
              type="password"
              placeholder="Confirm your password"
              [(model)]="confirmPassword"
              [required]="true"
              [errorMessage]="confirmPasswordError()"
              [showPasswordToggle]="true"
            />

            <div class="register-page_terms">
              <label class="register-page_terms-label">
                <input
                  type="checkbox"
                  class="register-page_terms-checkbox"
                  [checked]="acceptedTerms()"
                  (change)="acceptedTerms.set($any($event.target).checked)"
                />
                <span class="register-page_terms-text">
                  I agree to the
                  <a href="/terms" target="_blank" class="register-page_terms-link"
                    >Terms of Service</a
                  >
                  and
                  <a href="/privacy" target="_blank" class="register-page_terms-link"
                    >Privacy Policy</a
                  >
                </span>
              </label>
              @if (termsError()) {
                <p class="register-page_terms-error">{{ termsError() }}</p>
              }
            </div>

            <div class="register-page_actions">
              <lib-button
                variant="primary"
                type="submit"
                [loading]="isSubmitting()"
                [disabled]="!isFormValid()"
                class="register-page_submit-button"
              >
                Create Account
              </lib-button>
            </div>
          </form>

          <div class="register-page_footer">
            <p class="register-page_footer-text">
              Already have an account?
              <a routerLink="/login" class="register-page_link">Sign in</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .register-page {
        @apply min-h-screen;
        @apply flex items-center justify-center;
        @apply px-4;
        @apply py-12;
        @apply bg-bg-primary;
      }

      .register-page_container {
        @apply w-full;
        @apply max-w-md;
      }

      .register-page_content {
        @apply flex flex-col;
        @apply gap-8;
        @apply p-8;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .register-page_title {
        @apply text-3xl font-bold;
        @apply mb-2;
        @apply text-text-primary;
        margin: 0;
      }

      .register-page_subtitle {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .register-page_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .register-page_terms {
        @apply flex flex-col;
        @apply gap-2;
      }

      .register-page_terms-label {
        @apply flex items-start;
        @apply gap-2;
        @apply cursor-pointer;
      }

      .register-page_terms-checkbox {
        @apply mt-1;
        @apply cursor-pointer;
        accent-color: var(--color-primary-600);
      }

      .register-page_terms-text {
        @apply text-sm;
        @apply text-text-secondary;
        @apply leading-normal;
      }

      .register-page_terms-link {
        @apply font-medium;
        @apply text-primary-600;
        text-decoration: none;
      }

      .register-page_terms-link:hover {
        @apply text-primary-700;
        text-decoration: underline;
      }

      .register-page_terms-error {
        @apply text-sm;
        @apply text-error-600;
        margin: 0;
        @apply ml-6;
      }

      .register-page_actions {
        @apply flex flex-col;
        @apply gap-3;
        @apply pt-2;
      }

      .register-page_submit-button {
        @apply w-full;
      }

      .register-page_footer {
        @apply text-center;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .register-page_footer-text {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .register-page_link {
        @apply font-medium;
        @apply text-primary-600;
        text-decoration: none;
      }

      .register-page_link:hover {
        @apply text-primary-700;
        text-decoration: underline;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RegisterPage {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  readonly name = signal('');
  readonly email = signal('');
  readonly password = signal('');
  readonly confirmPassword = signal('');
  readonly acceptedTerms = signal(false);
  readonly isSubmitting = signal(false);

  readonly nameError = computed(() => {
    const value = this.name();
    if (!value.trim()) {
      return 'Name is required';
    }
    if (value.trim().length < 2) {
      return 'Name must be at least 2 characters';
    }
    return '';
  });

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

  readonly termsError = computed(() => {
    if (!this.acceptedTerms() && (this.name() || this.email() || this.password())) {
      return 'You must accept the terms of service to continue';
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
      !this.nameError() &&
      !this.emailError() &&
      !this.passwordError() &&
      !this.confirmPasswordError() &&
      !this.termsError() &&
      this.name().trim().length > 0 &&
      this.email().trim().length > 0 &&
      this.password().trim().length > 0 &&
      this.confirmPassword().trim().length > 0 &&
      this.acceptedTerms()
    );
  });

  async handleSubmit(): Promise<void> {
    if (!this.isFormValid()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      await firstValueFrom(
        this.authService.register({
          name: this.name().trim(),
          email: this.email().trim(),
          password: this.password(),
        }),
      );

      this.toast.success('Account created successfully!');
      this.router.navigate(['/app']);
    } catch (error) {
      // Error is already handled by error interceptor
      console.error('Registration failed:', error);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
