import {
  Component,
  ChangeDetectionStrategy,
  computed,
  effect,
  inject,
  input,
  signal,
  untracked,
} from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { LabelService } from '../../../../application/services/label.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-edit-label-modal',
  standalone: true,
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{
        'projects.settings.labels.editModal.title' | translate
      }}</lib-modal-header>
      <lib-modal-content>
        <form class="edit-label-form" (ngSubmit)="handleSubmit()">
          <lib-input
            [label]="'projects.settings.labels.createModal.nameLabel' | translate"
            [placeholder]="'projects.settings.labels.createModal.namePlaceholder' | translate"
            [(model)]="name"
            [required]="true"
            [errorMessage]="nameError()"
            [helperText]="'projects.settings.labels.createModal.nameHelper' | translate"
          />
          <lib-input
            [label]="'projects.settings.labels.createModal.colorLabel' | translate"
            [placeholder]="'projects.settings.labels.createModal.colorPlaceholder' | translate"
            [(model)]="color"
            [errorMessage]="colorError()"
            [helperText]="'projects.settings.labels.createModal.colorHelper' | translate"
          />
        </form>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isSaving()">
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button
          variant="primary"
          (clicked)="handleSubmit()"
          [loading]="isSaving()"
          [disabled]="!isValid()"
        >
          {{ 'common.saveChanges' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .edit-label-form {
        @apply flex flex-col gap-4;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditLabelModal {
  private readonly modal = inject(Modal);
  private readonly labelService = inject(LabelService);
  private readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);

  readonly labelId = input.required<string>();
  readonly initialName = input.required<string>();
  readonly initialColor = input.required<string>();
  readonly existingLabelNames = input<string[]>([]);

  readonly name = signal('');
  readonly color = signal('');
  readonly isSaving = signal(false);

  private readonly seedFromInputs = effect(() => {
    const id = this.labelId();
    const n = this.initialName();
    const c = this.initialColor();
    void id;
    untracked(() => {
      this.name.set(n);
      this.color.set(c);
    });
  });

  readonly nameError = computed(() => {
    const value = this.name().trim();
    if (!value) {
      return this.translateService.instant('projects.settings.labels.createModal.nameRequired');
    }

    const initial = this.initialName().trim().toLowerCase();
    const existing = new Set(
      this.existingLabelNames()
        .map((n) => n.trim().toLowerCase())
        .filter((n) => n !== initial),
    );
    if (existing.has(value.toLowerCase())) {
      return this.translateService.instant('projects.settings.labels.createModal.nameDuplicate');
    }

    return '';
  });

  readonly colorError = computed(() => {
    const value = this.color().trim();
    if (!value) {
      return this.translateService.instant('projects.settings.labels.createModal.colorRequired');
    }

    const hexColorPattern = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/;
    if (!hexColorPattern.test(value)) {
      return this.translateService.instant('projects.settings.labels.createModal.colorInvalid');
    }

    return '';
  });

  readonly isValid = computed(() => !this.nameError() && !this.colorError());

  handleCancel(): void {
    this.modal.close(false);
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    this.isSaving.set(true);

    try {
      await this.labelService.updateLabel(this.labelId(), {
        name: this.name().trim(),
        color: this.color().trim(),
      });
      this.toast.success(
        this.translateService.instant('projects.settings.labels.editModal.saveSuccess'),
      );
      this.modal.close(true);
    } catch (error) {
      console.error('Failed to update label:', error);
      const message =
        error instanceof Error
          ? error.message
          : this.translateService.instant('projects.settings.labels.editModal.saveError');
      this.toast.error(message);
    } finally {
      this.isSaving.set(false);
    }
  }
}
