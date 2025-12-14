import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  ViewContainerRef,
  effect,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Button, Input, LoadingState, ErrorState, Modal, ToastService } from 'shared-ui';
import { SpaceService } from '../../application/services/space.service';
import { NavigationService } from '../../application/services/navigation.service';
import { DeleteSpaceModal } from '../components/delete-space-modal';
import { BackToPage } from '../components/back-to-page';

@Component({
  selector: 'app-space-settings-page',
  imports: [Button, Input, LoadingState, ErrorState, BackToPage],
  template: `
    <div class="space-settings-page">
      <div class="space-settings-page_header">
        <div class="space-settings-page_header-content">
          <div>
            <app-back-to-page label="Back to Space" (onClick)="handleBackToSpace()" />
            <h1 class="space-settings-page_title">Space Settings</h1>
            <p class="space-settings-page_subtitle">Manage your space details and configuration.</p>
          </div>
        </div>
      </div>

      <div class="space-settings-page_content">
        @if (spaceService.isFetchingSpace()) {
          <lib-loading-state message="Loading space..." />
        } @else if (spaceService.hasSpaceError()) {
          <lib-error-state
            title="Failed to Load Space"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else if (!space()) {
          <lib-error-state
            title="Space Not Found"
            message="The space you're looking for doesn't exist or you don't have access to it."
            [showRetry]="false"
          />
        } @else {
          <div class="space-settings-page_container">
            <!-- Space Details Section -->
            <div class="space-settings-page_section">
              <h2 class="space-settings-page_section-title">Space Details</h2>
              <form class="space-settings-page_form" (ngSubmit)="handleSaveSpace()">
                <lib-input
                  label="Space Name"
                  placeholder="Enter space name"
                  [(model)]="name"
                  [required]="true"
                  [errorMessage]="nameError()"
                  helperText="The display name for your space"
                />
                <lib-input
                  label="Space Key"
                  placeholder="SPACE"
                  [(model)]="key"
                  [readonly]="true"
                  helperText="Space key cannot be changed after creation"
                />
                <lib-input
                  label="Description"
                  type="textarea"
                  placeholder="Describe your space (optional)"
                  [(model)]="description"
                  [rows]="4"
                  helperText="Optional description of your space"
                />
                <div class="space-settings-page_form-actions">
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

            <!-- Danger Zone Section -->
            <div class="space-settings-page_section space-settings-page_section--danger">
              <h2 class="space-settings-page_section-title">Danger Zone</h2>
              <div class="space-settings-page_danger-content">
                <div>
                  <h3 class="space-settings-page_danger-title">Delete Space</h3>
                  <p class="space-settings-page_danger-description">
                    Once you delete a space, there is no going back. All pages in this space will
                    also be deleted. Please be certain.
                  </p>
                </div>
                <lib-button
                  variant="danger"
                  size="md"
                  (clicked)="handleDeleteSpace()"
                  [disabled]="isDeleting()"
                >
                  Delete Space
                </lib-button>
              </div>
            </div>
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .space-settings-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .space-settings-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .space-settings-page_header-content {
        @apply max-w-7xl mx-auto;
      }

      .space-settings-page_title {
        @apply text-3xl font-bold mb-2;
        @apply text-text-primary;
        margin: 0;
      }

      .space-settings-page_subtitle {
        @apply text-base;
        @apply text-text-secondary;
        margin: 0;
      }

      .space-settings-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .space-settings-page_container {
        @apply max-w-4xl mx-auto;
        @apply flex flex-col;
        @apply gap-8;
      }

      .space-settings-page_section {
        @apply flex flex-col;
        @apply gap-6;
        @apply p-6;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
      }

      .space-settings-page_section--danger {
        @apply border-error;
      }

      .space-settings-page_section-title {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .space-settings-page_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .space-settings-page_form-actions {
        @apply flex items-center;
        @apply gap-3;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .space-settings-page_danger-content {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .space-settings-page_danger-title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0 0 0.5rem 0;
      }

      .space-settings-page_danger-description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SpaceSettingsPage {
  readonly spaceService = inject(SpaceService);
  readonly navigationService = inject(NavigationService);
  readonly route = inject(ActivatedRoute);
  readonly router = inject(Router);
  readonly modal = inject(Modal);
  readonly toast = inject(ToastService);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly spaceId = computed(() => {
    return this.navigationService.currentSpaceId() || '';
  });
  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });
  readonly space = computed(() => this.spaceService.currentSpace());

  readonly name = signal('');
  readonly key = signal('');
  readonly description = signal('');
  readonly isSaving = signal(false);
  readonly isDeleting = signal(false);
  readonly originalName = signal('');
  readonly originalDescription = signal('');

  readonly nameError = computed(() => {
    const value = this.name();
    if (!value.trim()) {
      return 'Space name is required';
    }
    if (value.trim().length < 3) {
      return 'Space name must be at least 3 characters';
    }
    return '';
  });

  readonly isFormValid = computed(() => {
    return !this.nameError() && this.name().trim().length > 0;
  });

  readonly hasChanges = computed(() => {
    return (
      this.name().trim() !== this.originalName() ||
      this.description().trim() !== this.originalDescription()
    );
  });

  readonly errorMessage = computed(() => {
    const error = this.spaceService.spaceError();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading the space.';
    }
    return 'An unknown error occurred.';
  });

  private readonly initializeFormEffect = effect(
    () => {
      const space = this.space();
      if (space) {
        this.name.set(space.name);
        this.key.set(space.key);
        this.description.set(space.description || '');
        this.originalName.set(space.name);
        this.originalDescription.set(space.description || '');
      }
    },
    { allowSignalWrites: true },
  );

  async handleSaveSpace(): Promise<void> {
    if (!this.isFormValid() || !this.hasChanges()) {
      return;
    }

    const id = this.spaceId();
    if (!id) {
      return;
    }

    this.isSaving.set(true);

    try {
      await this.spaceService.updateSpace(id, {
        name: this.name().trim(),
        description: this.description().trim() || undefined,
      });
      this.originalName.set(this.name().trim());
      this.originalDescription.set(this.description().trim());
      this.toast.success('Space updated successfully!');
    } catch (error) {
      console.error('Failed to update space:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update space. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSaving.set(false);
    }
  }

  handleReset(): void {
    const space = this.space();
    if (space) {
      this.name.set(space.name);
      this.description.set(space.description || '');
      this.originalName.set(space.name);
      this.originalDescription.set(space.description || '');
    }
  }

  handleDeleteSpace(): void {
    const id = this.spaceId();
    const orgId = this.organizationId();
    if (!id || !orgId) {
      return;
    }

    this.modal.open(DeleteSpaceModal, this.viewContainerRef, {
      size: 'md',
      data: { spaceId: id, spaceName: this.space()?.name || 'this space', organizationId: orgId },
    });
  }

  handleRetry(): void {
    this.spaceService.reloadCurrentSpace();
  }

  handleBackToSpace(): void {
    const orgId = this.organizationId();
    if (orgId) {
      this.navigationService.navigateToOrganizationSpaces(orgId);
    }
  }
}
