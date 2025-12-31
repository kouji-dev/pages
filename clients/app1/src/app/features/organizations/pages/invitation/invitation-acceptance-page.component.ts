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
import { AuthService } from '../../../../core/auth/auth.service';
import { OrganizationInvitationsService } from '../../../../application/services/organization-invitations.service';
import { PublicNav } from '../../../../presentation/components/public-nav'; // Should ideally be shared
import { Footer } from '../../../../presentation/components/footer'; // Should ideally be shared
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-invitation-acceptance-page',
  imports: [PublicNav, Footer, Button, Icon, LoadingState, ErrorState, TranslatePipe],
  template: `
    <div class="invitation-acceptance-page">
      <app-public-nav />
      <main class="invitation-acceptance-page_main">
        <div class="invitation-acceptance-page_container">
          @if (isLoading()) {
            <lib-loading-state [message]="'auth.invitationAcceptance.loading' | translate" />
          } @else if (hasError()) {
            <lib-error-state
              [title]="errorTitle()"
              [message]="errorMessage()"
              [retryLabel]="isAuthenticated() ? ('common.tryAgain' | translate) : ''"
              [showRetry]="isAuthenticated()"
              (onRetry)="handleAccept()"
            />
          } @else if (isAccepted()) {
            <div class="invitation-acceptance-page_success">
              <div class="invitation-acceptance-page_success-icon">
                <lib-icon name="circle-check" size="xl" color="success" />
              </div>
              <h1 class="invitation-acceptance-page_success-title">
                {{ 'auth.invitationAcceptance.successTitle' | translate }}
              </h1>
              @if (acceptedOrganization()) {
                <p class="invitation-acceptance-page_success-message">
                  {{
                    'auth.invitationAcceptance.successMessage'
                      | translate
                        : {
                            orgName: acceptedOrganization()?.organization_name,
                            role: acceptedOrganization()?.role,
                          }
                  }}
                </p>
                <div class="invitation-acceptance-page_success-actions">
                  <lib-button
                    variant="primary"
                    size="lg"
                    [link]="['/app/organizations']"
                    leftIcon="arrow-right"
                  >
                    {{ 'auth.invitationAcceptance.goToOrganizations' | translate }}
                  </lib-button>
                </div>
              }
            </div>
          } @else {
            <div class="invitation-acceptance-page_content">
              <div class="invitation-acceptance-page_icon">
                <lib-icon name="mail" size="xl" color="primary" />
              </div>
              <h1 class="invitation-acceptance-page_title">
                {{ 'auth.invitationAcceptance.title' | translate }}
              </h1>
              <p class="invitation-acceptance-page_description">
                {{ 'auth.invitationAcceptance.description' | translate }}
              </p>

              @if (isAuthenticated()) {
                <div class="invitation-acceptance-page_authenticated">
                  <p class="invitation-acceptance-page_authenticated-message">
                    {{
                      'auth.invitationAcceptance.authenticatedMessage'
                        | translate: { email: currentUserEmail() }
                    }}
                  </p>
                  <lib-button
                    variant="primary"
                    size="lg"
                    (clicked)="handleAccept()"
                    [loading]="isAccepting()"
                    [disabled]="isAccepting()"
                    leftIcon="check"
                  >
                    {{ 'auth.invitationAcceptance.acceptInvitation' | translate }}
                  </lib-button>
                </div>
              } @else {
                <div class="invitation-acceptance-page_unauthenticated">
                  <p class="invitation-acceptance-page_unauthenticated-message">
                    {{ 'auth.invitationAcceptance.unauthenticatedMessage' | translate }}
                  </p>
                  <div class="invitation-acceptance-page_unauthenticated-actions">
                    <lib-button
                      variant="primary"
                      size="lg"
                      (clicked)="handleLogin()"
                      leftIcon="log-in"
                    >
                      {{ 'auth.login' | translate }}
                    </lib-button>
                    <lib-button
                      variant="secondary"
                      size="lg"
                      (clicked)="handleRegister()"
                      leftIcon="user-plus"
                    >
                      {{ 'auth.register.title' | translate }}
                    </lib-button>
                  </div>
                  <p class="invitation-acceptance-page_unauthenticated-note">
                    {{ 'auth.invitationAcceptance.unauthenticatedNote' | translate }}
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
        @apply bg-background;
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
        @apply bg-card;
        @apply border border-border;
      }

      .invitation-acceptance-page_icon {
        @apply flex items-center justify-center;
        @apply w-16 h-16;
        @apply rounded-full;
        @apply bg-muted;
      }

      .invitation-acceptance-page_title {
        @apply text-2xl sm:text-3xl;
        @apply font-bold;
        @apply text-foreground;
        margin: 0;
      }

      .invitation-acceptance-page_description {
        @apply text-base;
        @apply text-muted-foreground;
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
        @apply text-muted-foreground;
        margin: 0;
      }

      .invitation-acceptance-page_authenticated-message strong {
        @apply text-foreground;
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
        @apply text-muted-foreground;
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
        @apply text-muted-foreground;
        margin: 0;
        @apply max-w-xs;
      }

      .invitation-acceptance-page_success {
        @apply flex flex-col items-center;
        @apply gap-6;
        @apply text-center;
        @apply p-8;
        @apply rounded-lg;
        @apply bg-card;
        @apply border border-border;
      }

      .invitation-acceptance-page_success-icon {
        @apply flex items-center justify-center;
        @apply w-16 h-16;
        @apply rounded-full;
        @apply bg-success/10;
      }

      .invitation-acceptance-page_success-title {
        @apply text-2xl sm:text-3xl;
        @apply font-bold;
        @apply text-foreground;
        margin: 0;
      }

      .invitation-acceptance-page_success-message {
        @apply text-base;
        @apply text-muted-foreground;
        margin: 0;
        @apply max-w-md;
      }

      .invitation-acceptance-page_success-message strong {
        @apply text-foreground;
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
  private readonly translateService = inject(TranslateService);

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
    if (!err) return this.translateService.instant('common.error');
    const message = err.message.toLowerCase();
    if (message.includes('expired'))
      return this.translateService.instant('auth.invitationAcceptance.errors.expired');
    if (message.includes('already accepted'))
      return this.translateService.instant('auth.invitationAcceptance.errors.alreadyAccepted');
    if (message.includes('not found'))
      return this.translateService.instant('auth.invitationAcceptance.errors.notFound');
    if (message.includes('email'))
      return this.translateService.instant('auth.invitationAcceptance.errors.emailMismatch');
    if (message.includes('already member'))
      return this.translateService.instant('auth.invitationAcceptance.errors.alreadyMember');
    return this.translateService.instant('auth.invitationAcceptance.errors.failed');
  });

  readonly errorMessage = computed(() => {
    const err = this.error();
    if (!err) return this.translateService.instant('common.unknownError');
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
      this.error.set(
        new Error(this.translateService.instant('auth.invitationAcceptance.errors.invalidToken')),
      );
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
      this.toast.success(this.translateService.instant('auth.invitationAcceptance.acceptSuccess'));
    } catch (error) {
      console.error('Failed to accept invitation:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('auth.invitationAcceptance.errors.failed');
      this.error.set(new Error(errorMessage));
      this.toast.error(errorMessage);
    } finally {
      this.isAccepting.set(false);
    }
  }
}
