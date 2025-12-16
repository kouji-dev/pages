import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { Button, Input, ToastService } from 'shared-ui';
import { firstValueFrom } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { AuthService } from '../../../../core/auth/auth.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-reset-password-page',
  standalone: true,
  imports: [Button, Input, RouterLink, TranslatePipe],
  template: `
    <div class="reset-password-page">
      <div class="reset-password-page_container">
        <div class="reset-password-page_content">
          <h1 class="reset-password-page_title">{{ 'auth.resetPassword.title' | translate }}</h1>
          <p class="reset-password-page_subtitle">
            {{ 'auth.resetPassword.subtitle' | translate }}
          </p>

          @if (isInvalidToken()) {
            <div class="reset-password-page_error">
              <p class="reset-password-page_error-text">
                {{ 'auth.resetPassword.invalidToken' | translate }}
              </p>
              <lib-button variant="primary" [link]="'/forgot-password'">
                {{ 'auth.resetPassword.requestNewLink' | translate }}
              </lib-button>
            </div>
          } @else {
            <form
              class="reset-password-page_form"
              (ngSubmit)="handleSubmit()"
              (submit)="$event.preventDefault()"
            >
              <lib-input
                [label]="'auth.resetPassword.newPassword' | translate"
                type="password"
                [placeholder]="'auth.resetPassword.newPasswordPlaceholder' | translate"
                [(model)]="password"
                [required]="true"
                [errorMessage]="passwordError()"
                [showPasswordToggle]="true"
                [helperText]="passwordStrengthText()"
              />

              <lib-input
                [label]="'auth.resetPassword.confirmPassword' | translate"
                type="password"
                [placeholder]="'auth.resetPassword.confirmPasswordPlaceholder' | translate"
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
                  {{ 'auth.resetPassword.resetPassword' | translate }}
                </lib-button>
              </div>
            </form>
          }

          @if (isSuccess()) {
            <div class="reset-password-page_success">
              <p class="reset-password-page_success-text">
                {{ 'auth.resetPassword.successMessage' | translate }}
              </p>
              <lib-button variant="primary" [link]="'/login'">{{
                'auth.resetPassword.goToSignIn' | translate
              }}</lib-button>
            </div>
          }

          <div class="reset-password-page_footer">
            <a routerLink="/login" class="reset-password-page_link">{{
              'auth.resetPassword.backToSignIn' | translate
            }}</a>
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
        @apply bg-background;
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
        @apply border-border;
        @apply bg-muted;
      }

      .reset-password-page_title {
        @apply text-3xl font-bold;
        @apply mb-2;
        @apply text-foreground;
        margin: 0;
      }

      .reset-password-page_subtitle {
        @apply text-sm;
        @apply text-muted-foreground;
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
        @apply border-destructive/20;
        @apply bg-destructive/10;
      }

      .reset-password-page_error-text {
        @apply text-sm;
        @apply text-destructive;
        margin: 0;
      }

      .reset-password-page_success {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-4;
        @apply rounded-md;
        @apply border;
        @apply border-success/20;
        @apply bg-success/10;
      }

      .reset-password-page_success-text {
        @apply text-sm;
        @apply text-success;
        margin: 0;
      }

      .reset-password-page_footer {
        @apply text-center;
        @apply pt-4;
        @apply border-t;
        @apply border-border;
      }

      .reset-password-page_link {
        @apply text-sm;
        @apply font-medium;
        @apply text-primary;
        text-decoration: none;
      }

      .reset-password-page_link:hover {
        @apply text-primary/80;
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
  private readonly translateService = inject(TranslateService);

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
      return this.translateService.instant('auth.passwordRequired');
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
    const passwordValue = this.password();
    if (!value.trim()) {
      return this.translateService.instant('auth.confirmPasswordRequired');
    }
    if (value !== passwordValue) {
      return this.translateService.instant('auth.passwordsDoNotMatch');
    }
    return '';
  });

  readonly passwordStrengthText = computed(() => {
    const value = this.password();
    if (!value) {
      return this.translateService.instant('auth.resetPassword.passwordRequirements');
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
      return this.translateService.instant('auth.resetPassword.passwordStrengthWeak');
    } else if (strength <= 4) {
      return this.translateService.instant('auth.resetPassword.passwordStrengthMedium');
    } else {
      return this.translateService.instant('auth.resetPassword.passwordStrengthStrong');
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
      this.toast.success(this.translateService.instant('auth.resetPassword.resetSuccess'));
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
