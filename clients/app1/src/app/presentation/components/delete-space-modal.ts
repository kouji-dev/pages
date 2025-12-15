import { Component, ChangeDetectionStrategy, inject, input, signal, computed } from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { SpaceService } from '../../application/services/space.service';
import { NavigationService } from '../../application/services/navigation.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-delete-space-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{ 'spaces.modals.deleteSpace' | translate }}</lib-modal-header>
      <lib-modal-content>
        <div class="delete-space-modal_content">
          <p class="delete-space-modal_warning">
            {{ 'spaces.modals.deleteWarning' | translate: { name: spaceName() } }}
          </p>
          <p class="delete-space-modal_description">
            {{ 'spaces.modals.deleteDescription' | translate }}
          </p>
          <lib-input
            [label]="'spaces.modals.deleteConfirmLabel' | translate"
            [placeholder]="'spaces.modals.deleteConfirmPlaceholder' | translate"
            [(model)]="confirmationName"
            [helperText]="'spaces.modals.deleteConfirmHelper' | translate"
          />
        </div>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isDeleting()">
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button
          variant="danger"
          (clicked)="handleDelete()"
          [loading]="isDeleting()"
          [disabled]="!isConfirmed()"
        >
          {{ 'spaces.modals.deleteSpace' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .delete-space-modal_content {
        @apply flex flex-col;
        @apply gap-4;
      }

      .delete-space-modal_warning {
        @apply text-base;
        @apply text-text-primary;
        margin: 0;
      }

      .delete-space-modal_warning strong {
        @apply font-semibold;
      }

      .delete-space-modal_description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeleteSpaceModal {
  private readonly spaceService = inject(SpaceService);
  private readonly toast = inject(ToastService);
  private readonly navigationService = inject(NavigationService);
  private readonly modal = inject(Modal);
  private readonly translateService = inject(TranslateService);

  readonly spaceId = input.required<string>();
  readonly spaceName = input.required<string>();
  readonly organizationId = input.required<string>();

  readonly confirmationName = signal('');
  readonly isDeleting = signal(false);

  readonly isConfirmed = computed(() => {
    return this.confirmationName().trim() === this.spaceName().trim();
  });

  handleCancel(): void {
    this.modal.close();
  }

  async handleDelete(): Promise<void> {
    if (!this.isConfirmed()) {
      return;
    }

    this.isDeleting.set(true);

    try {
      await this.spaceService.deleteSpace(this.spaceId());
      this.toast.success(this.translateService.instant('spaces.modals.deleteSuccess'));
      this.modal.close();

      // Navigate to spaces list for current organization
      const orgId = this.organizationId();
      if (orgId) {
        this.navigationService.navigateToOrganizationSpaces(orgId);
      } else {
        this.navigationService.navigateToOrganizations();
      }
    } catch (error) {
      console.error('Failed to delete space:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('spaces.modals.deleteError');
      this.toast.error(errorMessage);
    } finally {
      this.isDeleting.set(false);
    }
  }
}
