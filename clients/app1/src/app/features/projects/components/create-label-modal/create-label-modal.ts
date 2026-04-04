import { Component, ChangeDetectionStrategy, computed, inject, input, signal } from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input } from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

export interface CreateLabelModalResult {
  name: string;
  color: string;
}

@Component({
  selector: 'app-create-label-modal',
  standalone: true,
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{
        'projects.settings.labels.createModal.title' | translate
      }}</lib-modal-header>
      <lib-modal-content>
        <form class="create-label-form" (ngSubmit)="handleSubmit()">
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
        <lib-button variant="secondary" (clicked)="handleCancel()">
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button variant="primary" (clicked)="handleSubmit()" [disabled]="!isValid()">
          {{ 'projects.settings.labels.createModal.submit' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .create-label-form {
        @apply flex flex-col gap-4;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CreateLabelModal {
  private readonly modal = inject(Modal);
  private readonly translateService = inject(TranslateService);

  readonly existingLabelNames = input<string[]>([]);

  readonly name = signal('');
  readonly color = signal('#64748B');

  readonly nameError = computed(() => {
    const value = this.name().trim();
    if (!value) {
      return this.translateService.instant('projects.settings.labels.createModal.nameRequired');
    }

    const existing = new Set(this.existingLabelNames().map((n) => n.trim().toLowerCase()));
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
    this.modal.close(null);
  }

  handleSubmit(): void {
    if (!this.isValid()) {
      return;
    }

    const payload: CreateLabelModalResult = {
      name: this.name().trim(),
      color: this.color().trim(),
    };
    this.modal.close(payload);
  }
}
