import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  effect,
} from '@angular/core';
import { Button, Icon, Input, LoadingState, ErrorState, ToastService } from 'shared-ui';
import { UserProfileService, UserProfile } from '../../application/services/user-profile.service';
import { ChangePasswordForm } from '../components/change-password-form';
import { AvatarUpload } from '../components/avatar-upload';

@Component({
  selector: 'app-profile-page',
  imports: [Button, Input, LoadingState, ErrorState, ChangePasswordForm, AvatarUpload],
  template: `
    <div class="profile-page">
      <div class="profile-page_header">
        <div class="profile-page_header-content">
          <div>
            <h1 class="profile-page_title">Profile</h1>
            <p class="profile-page_subtitle">Manage your account settings and preferences.</p>
          </div>
        </div>
      </div>

      <div class="profile-page_content">
        @if (userProfileService.isLoading()) {
          <lib-loading-state message="Loading profile..." />
        } @else if (userProfileService.hasError()) {
          <lib-error-state
            title="Failed to Load Profile"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else if (!userProfileService.userProfile()) {
          <lib-error-state
            title="Profile Not Found"
            message="Unable to load your profile. Please try again later."
            [showRetry]="false"
          />
        } @else {
          <div class="profile-page_container">
            <!-- Profile Information Section -->
            <div class="profile-page_section">
              <h2 class="profile-page_section-title">Profile Information</h2>
              <form class="profile-page_form" (ngSubmit)="handleSaveProfile()">
                <lib-input
                  label="Name"
                  placeholder="Enter your name"
                  [(model)]="name"
                  [required]="true"
                  [errorMessage]="nameError()"
                  helperText="Your display name"
                />
                <lib-input
                  label="Email"
                  placeholder="your@email.com"
                  [(model)]="email"
                  [readonly]="true"
                  helperText="Email cannot be changed here. Contact support to change your email."
                />
                <div class="profile-page_form-actions">
                  <lib-button
                    variant="primary"
                    type="submit"
                    [loading]="isSaving()"
                    [disabled]="!isFormValid() || !hasChanges()"
                  >
                    Save Changes
                  </lib-button>
                  <lib-button
                    variant="secondary"
                    (clicked)="handleReset()"
                    [disabled]="!hasChanges() || isSaving()"
                  >
                    Cancel
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
        background: var(--color-bg-primary);
      }

      .profile-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        border-bottom: 1px solid var(--color-border-default);
      }

      .profile-page_header-content {
        @apply max-w-4xl mx-auto;
      }

      .profile-page_title {
        @apply text-3xl font-bold mb-2;
        color: var(--color-text-primary);
        margin: 0;
      }

      .profile-page_subtitle {
        @apply text-base;
        color: var(--color-text-secondary);
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
        border-color: var(--color-border-default);
        background: var(--color-bg-primary);
      }

      .profile-page_section-title {
        @apply text-xl font-semibold;
        color: var(--color-text-primary);
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
        border-color: var(--color-border-default);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfilePage {
  readonly userProfileService = inject(UserProfileService);
  readonly toast = inject(ToastService);

  readonly name = signal('');
  readonly email = signal('');
  readonly isSaving = signal(false);
  readonly originalName = signal('');

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

  readonly isFormValid = computed(() => {
    return !this.nameError() && this.name().trim().length > 0;
  });

  readonly hasChanges = computed(() => {
    return this.name().trim() !== this.originalName();
  });

  readonly errorMessage = computed(() => {
    const error = this.userProfileService.error();
    if (error) {
      return error instanceof Error
        ? error.message
        : 'An error occurred while loading your profile.';
    }
    return 'An unknown error occurred.';
  });

  // Update form fields when profile loads
  private readonly initializeFormEffect = effect(
    () => {
      const profile = this.userProfileService.userProfile();
      if (profile) {
        this.name.set(profile.name);
        this.email.set(profile.email);
        this.originalName.set(profile.name);
      }
    },
    { allowSignalWrites: true },
  );

  async handleSaveProfile(): Promise<void> {
    if (!this.isFormValid() || !this.hasChanges()) {
      return;
    }

    this.isSaving.set(true);

    try {
      await this.userProfileService.updateProfile({
        name: this.name().trim(),
      });
      this.originalName.set(this.name().trim());
      this.toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to update profile:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update profile. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSaving.set(false);
    }
  }

  handleReset(): void {
    const profile = this.userProfileService.userProfile();
    if (profile) {
      this.name.set(profile.name);
      this.originalName.set(profile.name);
    }
  }

  handleRetry(): void {
    this.userProfileService.loadProfile();
  }
}
