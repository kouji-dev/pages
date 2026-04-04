import { Component, ChangeDetectionStrategy, inject, input, signal } from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { LabelService } from '../../../../application/services/label.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-delete-label-modal',
  standalone: true,
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{
        'projects.settings.labels.deleteModal.title' | translate
      }}</lib-modal-header>
      <lib-modal-content>
        <div class="delete-label-modal_content">
          <p class="delete-label-modal_message">
            {{ 'projects.settings.labels.deleteModal.message' | translate: { name: labelName() } }}
          </p>
          <p class="delete-label-modal_hint">
            {{ 'projects.settings.labels.deleteModal.hint' | translate }}
          </p>
        </div>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isDeleting()">
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button variant="destructive" (clicked)="handleDelete()" [loading]="isDeleting()">
          {{ 'projects.settings.labels.deleteModal.confirm' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .delete-label-modal_content {
        @apply flex flex-col gap-3;
      }

      .delete-label-modal_message {
        @apply text-base text-foreground;
        margin: 0;
      }

      .delete-label-modal_hint {
        @apply text-sm text-muted-foreground;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeleteLabelModal {
  private readonly labelService = inject(LabelService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);
  private readonly translateService = inject(TranslateService);

  readonly labelId = input.required<string>();
  readonly labelName = input.required<string>();

  readonly isDeleting = signal(false);

  handleCancel(): void {
    this.modal.close(false);
  }

  async handleDelete(): Promise<void> {
    this.isDeleting.set(true);

    try {
      await this.labelService.deleteLabel(this.labelId());
      this.toast.success(
        this.translateService.instant('projects.settings.labels.deleteModal.success'),
      );
      this.modal.close(true);
    } catch (error) {
      console.error('Failed to delete label:', error);
      const message =
        error instanceof Error
          ? error.message
          : this.translateService.instant('projects.settings.labels.deleteModal.error');
      this.toast.error(message);
    } finally {
      this.isDeleting.set(false);
    }
  }
}
