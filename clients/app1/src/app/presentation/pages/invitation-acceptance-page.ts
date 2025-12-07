import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
  computed,
  effect,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Button, Icon, LoadingState, ErrorState, ToastService } from 'shared-ui';
import { AuthService } from '../../application/services/auth.service';
import { OrganizationInvitationsService } from '../../application/services/organization-invitations.service';
import { PublicNav } from '../components/public-nav';
import { Footer } from '../components/footer';

@Component({
  selector: 'app-invitation-acceptance-page',
  imports: [PublicNav, Footer, Button, Icon, LoadingState, ErrorState],
  template: `
    <div class="invitation-acceptance-page">
      <app-public-nav />
      <main class="invitation-acceptance-page_main">
        <div class="invitation-acceptance-page_container">
          @if (isLoading()) {
            <lib-loading-state message="Loading invitation..." />
          } @else if (hasError()) {
            <lib-error-state
              [title]="errorTitle()"
              [message]="errorMessage()"
              [retryLabel]="isAuthenticated() ? 'Try Again' : ''"
              [showRetry]="isAuthenticated()"
              (onRetry)="handleAccept()"
            />
          } @else if (isAccepted()) {
            <div class="invitation-acceptance-page_success">
              <div class="invitation-acceptance-page_success-icon">
                <lib-icon name="circle-check" size="xl" color="success" />
              </div>
              <h1 class="invitation-acceptance-page_success-title">Invitation Accepted!</h1>
              @if (acceptedOrganization()) {
                <p class="invitation-acceptance-page_success-message">
                  You've successfully joined
                  <strong>{{ acceptedOrganization()?.organization_name }}</strong> as a
                  {{ acceptedOrganization()?.role }}.
                </p>
                <div class="invitation-acceptance-page_success-actions">
                  <lib-button
                    variant="primary"
                    size="lg"
                    [link]="['/app/organizations']"
                    leftIcon="arrow-right"
                  >
                    Go to Organizations
                  </lib-button>
                </div>
              }
            </div>
          } @else {
            <div class="invitation-acceptance-page_content">
              <div class="invitation-acceptance-page_icon">
                <lib-icon name="mail" size="xl" color="primary-500" />
              </div>
              <h1 class="invitation-acceptance-page_title">Organization Invitation</h1>
              <p class="invitation-acceptance-page_description">
                You've been invited to join an organization. Please log in or sign up to accept this
                invitation.
              </p>

              @if (isAuthenticated()) {
                <div class="invitation-acceptance-page_authenticated">
                  <p class="invitation-acceptance-page_authenticated-message">
                    You're logged in as <strong>{{ currentUserEmail() }}</strong
                    >. Click the button below to accept this invitation.
                  </p>
                  <lib-button
                    variant="primary"
                    size="lg"
                    (clicked)="handleAccept()"
                    [loading]="isAccepting()"
                    [disabled]="isAccepting()"
                    leftIcon="check"
                  >
                    Accept Invitation
                  </lib-button>
                </div>
              } @else {
                <div class="invitation-acceptance-page_unauthenticated">
                  <p class="invitation-acceptance-page_unauthenticated-message">
                    You need to log in or create an account to accept this invitation.
                  </p>
                  <div class="invitation-acceptance-page_unauthenticated-actions">
                    <lib-button
                      variant="primary"
                      size="lg"
                      (clicked)="handleLogin()"
                      leftIcon="log-in"
                    >
                      Log In
                    </lib-button>
                    <lib-button
                      variant="secondary"
                      size="lg"
                      (clicked)="handleRegister()"
                      leftIcon="user-plus"
                    >
                      Sign Up
                    </lib-button>
                  </div>
                  <p class="invitation-acceptance-page_unauthenticated-note">
                    After logging in or signing up, you'll be redirected back here to accept the
                    invitation.
                  </p>
                </div>
              }
            </div>
          }
        </div>
      </main>
      <app-footer />
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .invitation-acceptance-page {
        @apply min-h-screen;
        @apply flex flex-col;
        background: var(--color-bg-primary);
      }

      .invitation-acceptance-page_main {
        @apply flex-1;
        @apply flex items-center justify-center;
        @apply py-12 md:py-16;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .invitation-acceptance-page_container {
        @apply w-full;
        @apply max-w-md;
        @apply mx-auto;
      }

      .invitation-acceptance-page_content {
        @apply flex flex-col items-center;
        @apply gap-6;
        @apply text-center;
        @apply p-8;
        @apply rounded-lg;
        background: var(--color-bg-secondary);
        border: 1px solid var(--color-border-default);
      }

      .invitation-acceptance-page_icon {
        @apply flex items-center justify-center;
        @apply w-16 h-16;
        @apply rounded-full;
        background: var(--color-bg-tertiary);
      }

      .invitation-acceptance-page_title {
        @apply text-2xl sm:text-3xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .invitation-acceptance-page_description {
        @apply text-base;
        color: var(--color-text-secondary);
        margin: 0;
        @apply max-w-md;
      }

      .invitation-acceptance-page_authenticated {
        @apply w-full;
        @apply flex flex-col items-center;
        @apply gap-4;
        @apply mt-4;
      }

      .invitation-acceptance-page_authenticated-message {
        @apply text-sm;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .invitation-acceptance-page_authenticated-message strong {
        color: var(--color-text-primary);
        font-weight: 600;
      }

      .invitation-acceptance-page_unauthenticated {
        @apply w-full;
        @apply flex flex-col items-center;
        @apply gap-4;
        @apply mt-4;
      }

      .invitation-acceptance-page_unauthenticated-message {
        @apply text-sm;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .invitation-acceptance-page_unauthenticated-actions {
        @apply flex flex-col sm:flex-row items-center justify-center;
        @apply gap-3;
        @apply w-full;
        @apply mt-2;
      }

      .invitation-acceptance-page_unauthenticated-actions lib-button {
        @apply w-full sm:w-auto;
        @apply min-w-[120px];
      }

      .invitation-acceptance-page_unauthenticated-note {
        @apply text-xs;
        color: var(--color-text-tertiary);
        margin: 0;
        @apply max-w-xs;
      }

      .invitation-acceptance-page_success {
        @apply flex flex-col items-center;
        @apply gap-6;
        @apply text-center;
        @apply p-8;
        @apply rounded-lg;
        background: var(--color-bg-secondary);
        border: 1px solid var(--color-border-default);
      }

      .invitation-acceptance-page_success-icon {
        @apply flex items-center justify-center;
        @apply w-16 h-16;
        @apply rounded-full;
        background: var(--color-success-50);
      }

      .invitation-acceptance-page_success-title {
        @apply text-2xl sm:text-3xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .invitation-acceptance-page_success-message {
        @apply text-base;
        color: var(--color-text-secondary);
        margin: 0;
        @apply max-w-md;
      }

      .invitation-acceptance-page_success-message strong {
        color: var(--color-text-primary);
        font-weight: 600;
      }

      .invitation-acceptance-page_success-actions {
        @apply flex flex-col sm:flex-row items-center justify-center;
        @apply gap-3;
        @apply w-full;
        @apply mt-2;
      }

      .invitation-acceptance-page_success-actions lib-button {
        @apply w-full sm:w-auto;
        @apply min-w-[180px];
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InvitationAcceptancePage {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);
  private readonly invitationsService = inject(OrganizationInvitationsService);
  private readonly toast = inject(ToastService);

  readonly token = computed(() => {
    const token = this.route.snapshot.paramMap.get('token');
    return token || null;
  });

  readonly isAccepting = signal(false);
  readonly isAccepted = signal(false);
  readonly acceptedOrganization = signal<{
    organization_id: string;
    organization_name: string;
    organization_slug: string;
    role: string;
  } | null>(null);
  readonly error = signal<Error | null>(null);

  readonly isLoading = computed(() => this.isAccepting());
  readonly hasError = computed(() => this.error() !== null);
  readonly isAuthenticated = computed(() => this.authService.isAuthenticated());
  readonly currentUserEmail = computed(() => this.authService.getUser()?.email || '');

  readonly errorTitle = computed(() => {
    const err = this.error();
    if (!err) return 'Error';
    const message = err.message.toLowerCase();
    if (message.includes('expired')) return 'Invitation Expired';
    if (message.includes('already accepted')) return 'Invitation Already Accepted';
    if (message.includes('not found')) return 'Invitation Not Found';
    if (message.includes('email')) return 'Email Mismatch';
    if (message.includes('already member')) return 'Already a Member';
    return 'Failed to Accept Invitation';
  });

  readonly errorMessage = computed(() => {
    const err = this.error();
    if (!err) return 'An unknown error occurred';
    return err.message;
  });

  handleLogin(): void {
    const token = this.token();
    if (token) {
      this.router.navigate(['/login'], {
        queryParams: { returnUrl: `/invitations/${token}` },
      });
    } else {
      this.router.navigate(['/login']);
    }
  }

  handleRegister(): void {
    const token = this.token();
    if (token) {
      this.router.navigate(['/register'], {
        queryParams: { returnUrl: `/invitations/${token}` },
      });
    } else {
      this.router.navigate(['/register']);
    }
  }

  constructor() {
    // Auto-accept if user is already authenticated when component loads
    effect(() => {
      const token = this.token();
      const authenticated = this.isAuthenticated();
      if (token && authenticated && !this.isAccepted() && !this.isAccepting()) {
        this.handleAccept();
      }
    });
  }

  async handleAccept(): Promise<void> {
    const token = this.token();
    if (!token) {
      this.error.set(new Error('Invalid invitation token'));
      return;
    }

    if (!this.isAuthenticated()) {
      // Redirect to login with return URL
      this.handleLogin();
      return;
    }

    this.isAccepting.set(true);
    this.error.set(null);

    try {
      const result = await this.invitationsService.acceptInvitation(token);
      this.acceptedOrganization.set(result);
      this.isAccepted.set(true);
      this.toast.success('Invitation accepted successfully!');
    } catch (error) {
      console.error('Failed to accept invitation:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to accept invitation. Please try again.';
      this.error.set(new Error(errorMessage));
      this.toast.error(errorMessage);
    } finally {
      this.isAccepting.set(false);
    }
  }
}
