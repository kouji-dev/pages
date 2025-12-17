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
import { SpaceService } from '../../../../application/services/space.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { DeleteSpaceModal } from '../../components/delete-space-modal/delete-space-modal';
import { BackToPage } from '../../../../shared/components/back-to-page/back-to-page.component';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-space-settings-page',
  imports: [Button, Input, LoadingState, ErrorState, BackToPage, TranslatePipe],
  template: `
    <div class="space-settings-page">
      <div class="space-settings-page_header">
        <div class="space-settings-page_header-content">
          <div>
            <app-back-to-page
              [label]="'spaces.backToSpace' | translate"
              (onClick)="handleBackToSpace()"
            />
            <h1 class="space-settings-page_title">{{ 'spaces.settings.title' | translate }}</h1>
            <p class="space-settings-page_subtitle">{{ 'spaces.settings.subtitle' | translate }}</p>
          </div>
        </div>
      </div>

      <div class="space-settings-page_content">
        @if (spaceService.isFetchingSpace()) {
          <lib-loading-state [message]="'spaces.loadingSpace' | translate" />
        } @else if (spaceService.hasSpaceError()) {
          <lib-error-state
            [title]="'spaces.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else if (!space()) {
          <lib-error-state
            [title]="'spaces.notFound' | translate"
            [message]="'spaces.notFoundDescription' | translate"
            [showRetry]="false"
          />
        } @else {
          <div class="space-settings-page_container">
            <!-- Space Details Section -->
            <div class="space-settings-page_section">
              <h2 class="space-settings-page_section-title">
                {{ 'spaces.settings.details' | translate }}
              </h2>
              <form class="space-settings-page_form" (ngSubmit)="handleSaveSpace()">
                <lib-input
                  [label]="'spaces.settings.name' | translate"
                  [placeholder]="'spaces.settings.namePlaceholder' | translate"
                  [(model)]="name"
                  [required]="true"
                  [errorMessage]="nameError()"
                  [helperText]="'spaces.settings.nameHelper' | translate"
                />
                <lib-input
                  [label]="'spaces.settings.key' | translate"
                  placeholder="SPACE"
                  [(model)]="key"
                  [readonly]="true"
                  [helperText]="'spaces.settings.keyHelper' | translate"
                />
                <lib-input
                  [label]="'spaces.settings.description' | translate"
                  type="textarea"
                  [placeholder]="'spaces.settings.descriptionPlaceholder' | translate"
                  [(model)]="description"
                  [rows]="4"
                  [helperText]="'spaces.settings.descriptionHelper' | translate"
                />
                <div class="space-settings-page_form-actions">
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

            <!-- Danger Zone Section -->
            <div class="space-settings-page_section space-settings-page_section--danger">
              <h2 class="space-settings-page_section-title">
                {{ 'spaces.settings.dangerZone' | translate }}
              </h2>
              <div class="space-settings-page_danger-content">
                <div>
                  <h3 class="space-settings-page_danger-title">
                    {{ 'spaces.settings.deleteTitle' | translate }}
                  </h3>
                  <p class="space-settings-page_danger-description">
                    {{ 'spaces.settings.deleteDescription' | translate }}
                  </p>
                </div>
                <lib-button
                  variant="destructive"
                  size="md"
                  (clicked)="handleDeleteSpace()"
                  [disabled]="isDeleting()"
                >
                  {{ 'spaces.deleteSpace' | translate }}
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
        @apply bg-background;
      }

      .space-settings-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border;
      }

      .space-settings-page_header-content {
        @apply max-w-7xl mx-auto;
      }

      .space-settings-page_title {
        @apply text-3xl font-bold mb-2;
        @apply text-foreground;
        margin: 0;
      }

      .space-settings-page_subtitle {
        @apply text-base;
        @apply text-muted-foreground;
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
        @apply border-border;
        @apply bg-background;
      }

      .space-settings-page_section--danger {
        @apply border-destructive;
      }

      .space-settings-page_section-title {
        @apply text-xl font-semibold;
        @apply text-foreground;
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
        @apply border-border;
      }

      .space-settings-page_danger-content {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .space-settings-page_danger-title {
        @apply text-lg font-semibold;
        @apply text-foreground;
        margin: 0 0 0.5rem 0;
      }

      .space-settings-page_danger-description {
        @apply text-sm;
        @apply text-muted-foreground;
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
  private readonly translateService = inject(TranslateService);

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
      return this.translateService.instant('spaces.settings.nameRequired');
    }
    if (value.trim().length < 3) {
      return this.translateService.instant('spaces.settings.nameMinLength');
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
      return error instanceof Error
        ? error.message
        : this.translateService.instant('spaces.loadError');
    }
    return this.translateService.instant('common.unknownError');
  });

  private readonly initializeFormEffect = effect(() => {
    const space = this.space();
    if (space) {
      this.name.set(space.name);
      this.key.set(space.key);
      this.description.set(space.description || '');
      this.originalName.set(space.name);
      this.originalDescription.set(space.description || '');
    }
  });

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
      this.toast.success(this.translateService.instant('spaces.updateSuccess'));
    } catch (error) {
      console.error('Failed to update space:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('spaces.updateError');
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
