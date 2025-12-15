import { Component, ChangeDetectionStrategy, inject, input, computed } from '@angular/core';
import {
  Modal,
  ModalContainer,
  ModalHeader,
  ModalContent,
  ModalFooter,
  Button,
  Icon,
} from 'shared-ui';
import { Attachment } from '../../application/services/attachment.service';
import { AttachmentService } from '../../application/services/attachment.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-file-preview-modal',
  standalone: true,
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Icon, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>
        <div class="file-preview_header">
          <div class="file-preview_header-info">
            <lib-icon [name]="iconName()" size="md" />
            <span class="file-preview_header-name">{{ attachment().original_name }}</span>
          </div>
        </div>
      </lib-modal-header>
      <lib-modal-content>
        <div class="file-preview_content">
          @if (isImage()) {
            <img
              [src]="previewUrl()"
              [alt]="attachment().original_name"
              class="file-preview_image"
            />
          } @else if (isPdf()) {
            <iframe
              [src]="previewUrl()"
              class="file-preview_pdf"
              [title]="'attachments.pdfPreview' | translate"
            ></iframe>
          } @else {
            <div class="file-preview_unsupported">
              <lib-icon name="file" size="xl" />
              <p>{{ 'attachments.previewNotAvailable' | translate }}</p>
              <p class="file-preview_unsupported-hint">
                {{ 'attachments.previewHint' | translate }}
              </p>
            </div>
          }
        </div>
      </lib-modal-content>
      <lib-modal-footer>
        <a [href]="downloadUrl()" target="_blank" class="file-preview_download-link">
          <lib-button variant="primary">
            <lib-icon name="download" size="sm" />
            {{ 'attachments.download' | translate }}
          </lib-button>
        </a>
        <lib-button variant="secondary" (clicked)="handleClose()">
          {{ 'common.close' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .file-preview_header {
        @apply flex items-center justify-between;
        @apply w-full;
      }

      .file-preview_header-info {
        @apply flex items-center gap-2;
        @apply flex-1;
        @apply min-w-0;
      }

      .file-preview_header-name {
        @apply font-medium;
        @apply text-text-primary;
        @apply truncate;
      }

      .file-preview_content {
        @apply flex items-center justify-center;
        @apply min-h-[400px];
        @apply max-h-[70vh];
        @apply overflow-auto;
      }

      .file-preview_image {
        @apply max-w-full;
        @apply max-h-full;
        @apply object-contain;
      }

      .file-preview_pdf {
        @apply w-full;
        @apply h-[600px];
        @apply border;
        @apply border-border-default;
        @apply rounded;
      }

      .file-preview_unsupported {
        @apply flex flex-col;
        @apply items-center;
        @apply gap-4;
        @apply py-12;
        @apply text-center;
      }

      .file-preview_unsupported p {
        @apply text-text-primary;
        margin: 0;
      }

      .file-preview_unsupported-hint {
        @apply text-sm;
        @apply text-text-secondary;
      }

      .file-preview_download-link {
        text-decoration: none;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FilePreviewModal {
  private readonly modal = inject(Modal);
  private readonly attachmentService = inject(AttachmentService);

  readonly attachment = input.required<Attachment>();

  readonly previewUrl = computed(() => {
    const att = this.attachment();
    if (!att) return '';
    return this.attachmentService.getDownloadUrl(att.id);
  });

  readonly downloadUrl = computed(() => {
    const att = this.attachment();
    if (!att) return '';
    return this.attachmentService.getDownloadUrl(att.id);
  });

  readonly isImage = computed(() => {
    const att = this.attachment();
    return att ? att.mime_type.startsWith('image/') : false;
  });

  readonly isPdf = computed(() => {
    const att = this.attachment();
    return att ? att.mime_type === 'application/pdf' : false;
  });

  readonly iconName = computed(() => {
    if (this.isImage()) return 'image';
    if (this.isPdf()) return 'file-text';
    return 'file';
  });

  handleClose(): void {
    this.modal.close();
  }
}
