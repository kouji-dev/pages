import { Component, ChangeDetectionStrategy, inject, input, signal, computed } from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button } from 'shared-ui';
import { Organization } from '../../application/services/organization.service';

export interface DeleteOrganizationModalData {
  organization: Organization;
}

@Component({
  selector: 'app-delete-organization-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button],
  template: `
    <lib-modal-container>
      <lib-modal-header>Delete Organization</lib-modal-header>
      <lib-modal-content>
        <p>
          Are you sure you want to delete <strong>{{ organization()?.name }}</strong
          >? This action cannot be undone.
        </p>
        <p>This will permanently delete:</p>
        <ul>
          <li>The organization and all its data</li>
          <li>All projects, issues, and pages</li>
          <li>All member associations</li>
        </ul>
        <p class="delete-org-modal_warning">
          <strong>Warning:</strong> This action is permanent and irreversible.
        </p>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isDeleting()">
          Cancel
        </lib-button>
        <lib-button variant="danger" (clicked)="handleConfirm()" [loading]="isDeleting()">
          Delete Organization
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .delete-org-modal_warning {
        @apply text-sm font-medium;
        @apply text-error;
        margin: 1rem 0 0 0;
      }

      .delete-org-modal_warning ul {
        @apply list-disc list-inside;
        @apply mt-2 mb-4;
        @apply text-sm;
        @apply text-text-secondary;
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
