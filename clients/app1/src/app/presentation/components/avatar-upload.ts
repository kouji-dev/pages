import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { Button, Icon, ToastService } from 'shared-ui';
import { UserProfileService } from '../../application/services/user-profile.service';

@Component({
  selector: 'app-avatar-upload',
  standalone: true,
  imports: [Button, Icon],
  template: `
    <div class="avatar-upload">
      <h2 class="avatar-upload_title">Avatar</h2>
      <p class="avatar-upload_description">Upload a profile picture to personalize your account.</p>

      <div class="avatar-upload_content">
        <div class="avatar-upload_preview">
          @if (displayUrl()) {
            <div class="avatar-upload_preview-image-wrapper">
              <img [src]="displayUrl()" [alt]="userName()" class="avatar-upload_preview-image" />
              @if (isUploading()) {
                <div class="avatar-upload_preview-overlay">
                  <lib-icon name="loader" size="lg" animation="spin" />
                  <span class="avatar-upload_preview-overlay-text">Uploading...</span>
                </div>
              }
            </div>
          } @else {
            <div class="avatar-upload_preview-placeholder">
              @if (userName()) {
                <span class="avatar-upload_preview-placeholder-text">{{ initials() }}</span>
              } @else {
                <lib-icon name="user" size="xl" />
              }
            </div>
          }
        </div>

        <div class="avatar-upload_actions">
          <label
            class="avatar-upload_file-label"
            [class.avatar-upload_file-label--disabled]="isUploading() || isDeleting()"
          >
            <input
              #fileInput
              type="file"
              accept="image/*"
              class="avatar-upload_file-input"
              [disabled]="isUploading() || isDeleting()"
              (change)="handleFileSelect($event)"
            />
            <lib-button
              variant="secondary"
              [disabled]="isUploading() || isDeleting()"
              leftIcon="upload"
            >
              {{ hasAvatar() ? 'Change Avatar' : 'Upload Avatar' }}
            </lib-button>
          </label>

          @if (hasAvatar() && !previewUrl()) {
            <lib-button
              variant="danger"
              [disabled]="isUploading() || isDeleting()"
              [loading]="isDeleting()"
              (clicked)="handleRemoveAvatar()"
              leftIcon="trash"
            >
              Remove Avatar
            </lib-button>
          }
        </div>

        @if (fileError()) {
          <div class="avatar-upload_error">
            <lib-icon name="circle-alert" size="sm" />
            <span>{{ fileError() }}</span>
          </div>
        }

        <div class="avatar-upload_info">
          <lib-icon name="info" size="sm" />
          <span>Accepted formats: JPG, PNG, GIF. Maximum file size: 5MB.</span>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .avatar-upload {
        @apply flex flex-col;
        @apply gap-6;
      }

      .avatar-upload_title {
        @apply text-xl font-semibold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .avatar-upload_description {
        @apply text-sm;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .avatar-upload_content {
        @apply flex flex-col;
        @apply gap-4;
      }

      .avatar-upload_preview {
        @apply flex items-center justify-center;
        @apply w-32 h-32;
        @apply mx-auto;
      }

      .avatar-upload_preview-image-wrapper {
        @apply relative;
        @apply w-full h-full;
        @apply rounded-full;
        @apply overflow-hidden;
        border: 2px solid var(--color-border-default);
      }

      .avatar-upload_preview-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .avatar-upload_preview-overlay {
        @apply absolute inset-0;
        @apply flex flex-col items-center justify-center gap-2;
        @apply rounded-full;
        background: var(--color-bg-overlay);
      }

      .avatar-upload_preview-overlay-text {
        @apply text-sm font-medium;
        color: white;
      }

      .avatar-upload_preview-placeholder {
        @apply w-full h-full;
        @apply flex items-center justify-center;
        @apply rounded-full;
        @apply border-2 border-dashed;
        border-color: var(--color-border-default);
        background: var(--color-bg-tertiary);
      }

      .avatar-upload_preview-placeholder-text {
        @apply text-3xl font-bold;
        color: var(--color-text-primary);
      }

      .avatar-upload_actions {
        @apply flex items-center justify-center;
        @apply gap-3;
        @apply flex-wrap;
      }

      .avatar-upload_file-label {
        @apply cursor-pointer;
        @apply inline-block;
      }

      .avatar-upload_file-label--disabled {
        @apply cursor-not-allowed;
        opacity: 0.5;
      }

      .avatar-upload_file-input {
        @apply hidden;
      }

      .avatar-upload_error {
        @apply flex items-center gap-2;
        @apply p-3;
        @apply rounded-lg;
        @apply text-sm;
        background: var(--color-error-50);
        color: var(--color-error);
      }

      .avatar-upload_info {
        @apply flex items-center gap-2;
        @apply p-3;
        @apply rounded-lg;
        @apply text-sm;
        background: var(--color-bg-tertiary);
        color: var(--color-text-secondary);
      }

      .avatar-upload_info lib-icon {
        @apply flex-shrink-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AvatarUpload {
  readonly userProfileService = inject(UserProfileService);
  readonly toast = inject(ToastService);

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  readonly previewUrl = signal<string | null>(null);
  readonly selectedFile = signal<File | null>(null);
  readonly isUploading = signal(false);
  readonly isDeleting = signal(false);
  readonly fileError = signal<string | null>(null);

  readonly userProfile = this.userProfileService.userProfile;
  readonly userName = computed(() => this.userProfile()?.name || '');
  readonly currentAvatarUrl = computed(() => this.userProfile()?.avatarUrl);

  readonly initials = computed(() => {
    const name = this.userName();
    if (!name) {
      return 'U';
    }
    const nameParts = name.split(' ');
    const initials = nameParts
      .map((part) => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
    return initials || 'U';
  });

  readonly hasAvatar = computed(() => {
    return !!this.currentAvatarUrl();
  });

  readonly displayUrl = computed(() => {
    return this.previewUrl() || this.currentAvatarUrl() || null;
  });

  handleFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    if (!file) {
      return;
    }

    this.fileError.set(null);

    // Validate file type
    if (!file.type.startsWith('image/')) {
      this.fileError.set('Please select an image file');
      this.resetFileInput();
      return;
    }

    // Validate file size (5MB = 5 * 1024 * 1024 bytes)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      this.fileError.set('File size must be less than 5MB');
      this.resetFileInput();
      return;
    }

    // Create preview URL
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      this.previewUrl.set(result);
      this.selectedFile.set(file);
      // Auto-upload after preview is created
      this.uploadAvatar(file);
    };
    reader.onerror = () => {
      this.fileError.set('Failed to read file. Please try again.');
      this.resetFileInput();
    };
    reader.readAsDataURL(file);
  }

  async uploadAvatar(file: File): Promise<void> {
    this.isUploading.set(true);
    this.fileError.set(null);

    try {
      await this.userProfileService.uploadAvatar(file);
      this.toast.success('Avatar uploaded successfully!');
      // Clear preview URL after successful upload (will use the new avatar URL from server)
      this.previewUrl.set(null);
      this.selectedFile.set(null);
      this.resetFileInput();
    } catch (error) {
      console.error('Failed to upload avatar:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to upload avatar. Please try again.';
      this.fileError.set(errorMessage);
      this.toast.error(errorMessage);
      // Keep preview so user can retry
    } finally {
      this.isUploading.set(false);
    }
  }

  async handleRemoveAvatar(): Promise<void> {
    if (!confirm('Are you sure you want to remove your avatar?')) {
      return;
    }

    this.isDeleting.set(true);
    this.fileError.set(null);

    try {
      await this.userProfileService.deleteAvatar();
      this.toast.success('Avatar removed successfully!');
      this.previewUrl.set(null);
      this.selectedFile.set(null);
      this.resetFileInput();
    } catch (error) {
      console.error('Failed to remove avatar:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to remove avatar. Please try again.';
      this.fileError.set(errorMessage);
      this.toast.error(errorMessage);
    } finally {
      this.isDeleting.set(false);
    }
  }

  private resetFileInput(): void {
    if (this.fileInput?.nativeElement) {
      this.fileInput.nativeElement.value = '';
    }
  }
}
