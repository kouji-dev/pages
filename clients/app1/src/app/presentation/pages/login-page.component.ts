import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-login-page',
  imports: [RouterLink],
  template: `
    <div class="login-page">
      <div class="login-page_content">
        <h1 class="login-page_title">Login</h1>
        <p class="login-page_message">
          Login page will be implemented in task 1.1.3 (Authentication Frontend)
        </p>
        <a routerLink="/" class="login-page_link">Go to Home</a>
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
      }

      .login-page_content {
        @apply text-center;
        @apply max-w-md;
      }

      .login-page_title {
        @apply text-3xl font-bold;
        @apply mb-4;
        color: var(--color-text-primary);
      }

      .login-page_message {
        @apply mb-6;
        color: var(--color-text-secondary);
      }

      .login-page_link {
        @apply underline;
        color: var(--color-primary-600);
      }

      .login-page_link:hover {
        color: var(--color-primary-700);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginPage {}
