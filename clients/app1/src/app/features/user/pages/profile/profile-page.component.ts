import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  effect,
} from '@angular/core';
import { Button, Icon, Input, LoadingState, ErrorState, ToastService } from 'shared-ui';
import { UserStore, UserProfile } from '../../../../core/user/user.store';
import { ChangePasswordForm } from '../../components/change-password-form/change-password-form.component';
import { AvatarUpload } from '../../../../shared/components/avatar-upload/avatar-upload';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-profile-page',
  imports: [
    Button,
    Input,
    LoadingState,
    ErrorState,
    ChangePasswordForm,
    AvatarUpload,
    TranslatePipe,
  ],
  template: `
    <div class="profile-page">
      <div class="profile-page_header">
        <div class="profile-page_header-content">
          <div>
            <h1 class="profile-page_title">{{ 'profile.title' | translate }}</h1>
            <p class="profile-page_subtitle">{{ 'profile.subtitle' | translate }}</p>
          </div>
        </div>
      </div>

      <div class="profile-page_content">
        @if (userStore.isLoading()) {
          <lib-loading-state [message]="'profile.loading' | translate" />
        } @else if (userStore.hasError()) {
          <lib-error-state
            [title]="'profile.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else if (!userStore.userProfile()) {
          <lib-error-state
            [title]="'profile.notFound' | translate"
            [message]="'profile.notFoundDescription' | translate"
            [showRetry]="false"
          />
        } @else {
          <div class="profile-page_container">
            <!-- Profile Information Section -->
            <div class="profile-page_section">
              <h2 class="profile-page_section-title">{{ 'profile.information' | translate }}</h2>
              <form class="profile-page_form" (ngSubmit)="handleSaveProfile()">
                <lib-input
                  [label]="'profile.name' | translate"
                  [placeholder]="'profile.namePlaceholder' | translate"
                  [(model)]="name"
                  [required]="true"
                  [errorMessage]="nameError()"
                  [helperText]="'profile.nameHelper' | translate"
                />
                <lib-input
                  [label]="'profile.email' | translate"
                  [placeholder]="'profile.emailPlaceholder' | translate"
                  [(model)]="email"
                  [readonly]="true"
                  [helperText]="'profile.emailHelper' | translate"
                />
                <div class="profile-page_form-actions">
                  <lib-button
                    variant="primary"
                    type="submit"
                    [loading]="isSaving()"
                    [disabled]="!isFormValid() || !hasChanges()"
                  >
                    {{ 'common.saveChanges' | translate }}
                  </lib-button>
                  <lib-button
                    variant="secondary"
                    (clicked)="handleReset()"
                    [disabled]="!hasChanges() || isSaving()"
                  >
                    {{ 'common.cancel' | translate }}
                  </lib-button>
                </div>
              </form>
            </div>

            <!-- Change Password Section -->
            <div class="profile-page_section">
              <app-change-password-form />
            </div>

            <!-- Avatar Upload Section -->
            <div class="profile-page_section">
              <app-avatar-upload />
            </div>
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .profile-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-background;
      }

      .profile-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border;
      }

      .profile-page_header-content {
        @apply max-w-4xl mx-auto;
      }

      .profile-page_title {
        @apply text-3xl font-bold mb-2;
        @apply text-foreground;
        margin: 0;
      }

      .profile-page_subtitle {
        @apply text-base;
        @apply text-muted-foreground;
        margin: 0;
      }

      .profile-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .profile-page_container {
        @apply max-w-4xl mx-auto;
        @apply flex flex-col;
        @apply gap-8;
      }

      .profile-page_section {
        @apply flex flex-col;
        @apply gap-6;
        @apply p-6;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-card;
      }

      .profile-page_section-title {
        @apply text-xl font-semibold;
        @apply text-foreground;
        margin: 0;
      }

      .profile-page_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .profile-page_form-actions {
        @apply flex items-center;
        @apply gap-3;
        @apply pt-4;
        @apply border-t;
        @apply border-border;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfilePage {
  readonly userStore = inject(UserStore);
  readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);

  readonly name = signal('');
  readonly email = signal('');
  readonly isSaving = signal(false);
  readonly originalName = signal('');

  readonly nameError = computed(() => {
    const value = this.name();
    if (!value.trim()) {
      return this.translateService.instant('profile.nameRequired');
    }
    if (value.trim().length < 2) {
      return this.translateService.instant('profile.nameMinLength');
    }
    return '';
  });

  readonly isFormValid = computed(() => {
    return !this.nameError() && this.name().trim().length > 0;
  });

  readonly hasChanges = computed(() => {
    return this.name().trim() !== this.originalName();
  });

  readonly errorMessage = computed(() => {
    const error = this.userStore.error();
    if (error) {
      return error instanceof Error
        ? error.message
        : this.translateService.instant('profile.loadError');
    }
    return this.translateService.instant('common.unknownError');
  });

  // Update form fields when profile loads
  private readonly initializeFormEffect = effect(() => {
    const profile = this.userStore.userProfile();
    if (profile) {
      this.name.set(profile.name);
      this.email.set(profile.email);
      this.originalName.set(profile.name);
    }
  });

  async handleSaveProfile(): Promise<void> {
    if (!this.isFormValid() || !this.hasChanges()) {
      return;
    }

    this.isSaving.set(true);

    try {
      await this.userStore.updateProfile({
        name: this.name().trim(),
      });
      this.originalName.set(this.name().trim());
      this.toast.success(this.translateService.instant('profile.updateSuccess'));
    } catch (error) {
      console.error('Failed to update profile:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('profile.updateError');
      this.toast.error(errorMessage);
    } finally {
      this.isSaving.set(false);
    }
  }

  handleReset(): void {
    const profile = this.userStore.userProfile();
    if (profile) {
      this.name.set(profile.name);
      this.originalName.set(profile.name);
    }
  }

  handleRetry(): void {
    this.userStore.loadProfile();
  }
}
