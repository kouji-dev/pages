import { Component, ChangeDetectionStrategy, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { Button, Input, ToastService } from 'shared-ui';
import { toObservable } from '@angular/core/rxjs-interop';
import { filter, take, timeout, catchError, of, switchMap } from 'rxjs';
import { AuthService } from '../../application/services/auth.service';
import { NavigationService } from '../../application/services/navigation.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [Button, Input, RouterLink, TranslatePipe],
  template: `
    <div class="login-page">
      <div class="login-page_container">
        <div class="login-page_content">
          <h1 class="login-page_title">{{ 'auth.welcomeBack' | translate }}</h1>
          <p class="login-page_subtitle">{{ 'auth.signInToContinue' | translate }}</p>

          <form
            class="login-page_form"
            (ngSubmit)="handleSubmit()"
            (submit)="$event.preventDefault()"
          >
            <lib-input
              [label]="'auth.email' | translate"
              type="email"
              [placeholder]="'auth.enterEmail' | translate"
              [(model)]="email"
              [required]="true"
              [errorMessage]="emailError()"
              [helperText]="'auth.emailHelper' | translate"
            />

            <lib-input
              [label]="'auth.password' | translate"
              type="password"
              [placeholder]="'auth.enterPassword' | translate"
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
                {{ 'auth.signIn' | translate }}
              </lib-button>
            </div>
          </form>

          <div class="login-page_footer">
            <p class="login-page_footer-text">
              {{ 'auth.dontHaveAccount' | translate }}
              <a routerLink="/register" class="login-page_link">{{ 'auth.signUp' | translate }}</a>
            </p>
            <a routerLink="/forgot-password" class="login-page_forgot-link">{{
              'auth.forgotPassword' | translate
            }}</a>
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
  private readonly navigationService = inject(NavigationService);
  private readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);

  readonly email = signal('');
  readonly password = signal('');
  readonly isSubmitting = signal(false);

  readonly emailError = computed(() => {
    const value = this.email();
    if (!value.trim()) {
      return this.translateService.instant('auth.emailRequired');
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value.trim())) {
      return this.translateService.instant('auth.emailInvalid');
    }
    return '';
  });

  readonly passwordError = computed(() => {
    const value = this.password();
    if (!value.trim()) {
      return this.translateService.instant('auth.passwordRequired');
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

    this.authService
      .login({
        email: this.email().trim(),
        password: this.password(),
      })
      .pipe(take(1))
      .subscribe({
        next: () => {
          this.toast.success(this.translateService.instant('auth.welcomeBack') + '!');
          // Navigate directly to organizations list
          this.navigationService.navigateToOrganizations();
          this.isSubmitting.set(false);
        },
        error: (error) => {
          console.error('Login failed:', error);
          this.isSubmitting.set(false);
        },
      });
  }
}
