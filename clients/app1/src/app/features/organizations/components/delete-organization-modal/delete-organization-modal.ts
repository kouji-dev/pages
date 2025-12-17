import { Component, ChangeDetectionStrategy, inject, input, signal, computed } from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button } from 'shared-ui';
import { Organization } from '../../../../application/services/organization.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

export interface DeleteOrganizationModalData {
  organization: Organization;
}

@Component({
  selector: 'app-delete-organization-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{
        'organizations.modals.deleteOrganization' | translate
      }}</lib-modal-header>
      <lib-modal-content>
        <p>
          {{ 'organizations.modals.deleteWarning' | translate: { name: organization()?.name } }}
        </p>
        <p>{{ 'organizations.modals.deleteWillDelete' | translate }}</p>
        <ul>
          <li>{{ 'organizations.modals.deleteItem1' | translate }}</li>
          <li>{{ 'organizations.modals.deleteItem2' | translate }}</li>
          <li>{{ 'organizations.modals.deleteItem3' | translate }}</li>
        </ul>
        <p class="delete-org-modal_warning">
          <strong>{{ 'organizations.modals.deleteWarningLabel' | translate }}</strong>
          {{ 'organizations.modals.deleteWarningText' | translate }}
        </p>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isDeleting()">
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button variant="destructive" (clicked)="handleConfirm()" [loading]="isDeleting()">
          {{ 'organizations.modals.deleteOrganization' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .delete-org-modal_warning {
        @apply text-sm font-medium;
        @apply text-destructive;
        margin: 1rem 0 0 0;
      }

      .delete-org-modal_warning ul {
        @apply list-disc list-inside;
        @apply mt-2 mb-4;
        @apply text-sm;
        @apply text-muted-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeleteOrganizationModal {
  readonly data = input<DeleteOrganizationModalData>();

  private readonly modal = inject(Modal);

  readonly isDeleting = signal(false);

  readonly organization = computed(() => this.data()?.organization);

  handleCancel(): void {
    this.modal.close({ confirmed: false });
  }

  async handleConfirm(): Promise<void> {
    const org = this.organization();
    if (!org) {
      return;
    }

    this.isDeleting.set(true);
    try {
      // Close with success payload - parent component will handle the actual deletion
      this.modal.close({ confirmed: true, organizationId: org.id });
    } catch (error) {
      console.error('Failed to delete organization:', error);
      // Close with error payload
      this.modal.close({ confirmed: false, error });
    } finally {
      this.isDeleting.set(false);
    }
  }
}
