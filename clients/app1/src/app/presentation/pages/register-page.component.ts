import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-register-page',
  imports: [RouterLink],
  template: `
    <div class="register-page">
      <div class="register-page_content">
        <h1 class="register-page_title">Sign Up</h1>
        <p class="register-page_message">
          Registration page will be implemented in task 1.1.3 (Authentication Frontend)
        </p>
        <a routerLink="/" class="register-page_link">Go to Home</a>
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
      }

      .register-page_content {
        @apply text-center;
        @apply max-w-md;
      }

      .register-page_title {
        @apply text-3xl font-bold;
        @apply mb-4;
        color: var(--color-text-primary);
      }

      .register-page_message {
        @apply mb-6;
        color: var(--color-text-secondary);
      }

      .register-page_link {
        @apply underline;
        color: var(--color-primary-600);
      }

      .register-page_link:hover {
        color: var(--color-primary-700);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RegisterPage {}
