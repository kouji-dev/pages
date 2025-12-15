import { Component, ChangeDetectionStrategy, inject, input, signal, computed } from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { ProjectService } from '../../application/services/project.service';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-delete-project-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{ 'projects.modals.deleteProject' | translate }}</lib-modal-header>
      <lib-modal-content>
        <div class="delete-project-modal_content">
          <p class="delete-project-modal_warning">
            {{ 'projects.modals.deleteWarning' | translate: { name: projectName() } }}
          </p>
          <p class="delete-project-modal_description">
            {{ 'projects.modals.deleteDescription' | translate }}
          </p>
          <lib-input
            [label]="'projects.modals.deleteConfirmLabel' | translate"
            [placeholder]="'projects.modals.deleteConfirmPlaceholder' | translate"
            [(model)]="confirmationName"
            [helperText]="'projects.modals.deleteConfirmHelper' | translate"
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
          {{ 'projects.modals.deleteProject' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .delete-project-modal_content {
        @apply flex flex-col;
        @apply gap-4;
      }

      .delete-project-modal_warning {
        @apply text-base;
        @apply text-text-primary;
        margin: 0;
      }

      .delete-project-modal_warning strong {
        @apply font-semibold;
      }

      .delete-project-modal_description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeleteProjectModal {
  private readonly projectService = inject(ProjectService);
  private readonly organizationService = inject(OrganizationService);
  private readonly toast = inject(ToastService);
  private readonly navigationService = inject(NavigationService);
  private readonly modal = inject(Modal);
  private readonly translateService = inject(TranslateService);

  readonly projectId = input.required<string>();
  readonly projectName = input.required<string>();

  readonly confirmationName = signal('');
  readonly isDeleting = signal(false);

  readonly isConfirmed = computed(() => {
    return this.confirmationName().trim() === this.projectName().trim();
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
      await this.projectService.deleteProject(this.projectId());
      this.toast.success(this.translateService.instant('projects.modals.deleteSuccess'));
      this.modal.close();

      // Navigate to projects list for current organization
      const orgId = this.organizationService.currentOrganization()?.id;
      if (orgId) {
        this.navigationService.navigateToOrganizationProjects(orgId);
      } else {
        this.navigationService.navigateToOrganizations();
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('projects.modals.deleteError');
      this.toast.error(errorMessage);
    } finally {
      this.isDeleting.set(false);
    }
  }
}
