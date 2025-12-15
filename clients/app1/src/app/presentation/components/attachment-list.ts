import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  input,
  signal,
  effect,
  ViewContainerRef,
} from '@angular/core';
import { Button, Icon, Modal } from 'shared-ui';
import { AttachmentService, Attachment } from '../../application/services/attachment.service';
import { FileUpload } from './file-upload';
import { FilePreviewModal } from './file-preview-modal';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-attachment-list',
  standalone: true,
  imports: [Button, Icon, FileUpload, TranslatePipe],
  template: `
    <div class="attachment-list">
      <div class="attachment-list_header">
        <h3 class="attachment-list_title">{{ 'attachments.title' | translate }}</h3>
      </div>

      <app-file-upload [issueId]="issueId()" />

      <div class="attachment-list_items">
        @if (attachmentService.isLoading()) {
          <div class="attachment-list_loading">{{ 'attachments.loading' | translate }}</div>
        } @else if (attachments().length === 0) {
          <div class="attachment-list_empty">{{ 'attachments.noAttachments' | translate }}</div>
        } @else {
          @for (attachment of attachments(); track attachment.id) {
            <div class="attachment-list_item">
              <div class="attachment-list_item-icon">
                @if (isImage(attachment.mime_type)) {
                  <div class="attachment-list_item-thumbnail">
                    <img
                      [src]="getDownloadUrl(attachment.id)"
                      [alt]="attachment.original_name"
                      (click)="handlePreview(attachment)"
                      class="attachment-list_thumbnail-image"
                    />
                  </div>
                } @else {
                  <lib-icon name="file" size="md" />
                }
              </div>
              <div class="attachment-list_item-info">
                <div class="attachment-list_item-name">{{ attachment.original_name }}</div>
                <div class="attachment-list_item-meta">
                  {{ formatFileSize(attachment.file_size) }} •
                  {{ formatDate(attachment.created_at) }}
                  @if (attachment.uploader_name) {
                    • {{ attachment.uploader_name }}
                  }
                </div>
              </div>
              <div class="attachment-list_item-actions">
                @if (isImage(attachment.mime_type) || attachment.mime_type === 'application/pdf') {
                  <lib-button variant="ghost" size="sm" (clicked)="handlePreview(attachment)">
                    {{ 'attachments.preview' | translate }}
                  </lib-button>
                }
                <a
                  [href]="getDownloadUrl(attachment.id)"
                  target="_blank"
                  class="attachment-list_download-link"
                >
                  <lib-button variant="ghost" size="sm">
                    {{ 'attachments.download' | translate }}
                  </lib-button>
                </a>
                <lib-button
                  variant="ghost"
                  size="sm"
                  (clicked)="handleDeleteAttachment(attachment)"
                >
                  {{ 'common.delete' | translate }}
                </lib-button>
              </div>
            </div>
          }
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .attachment-list {
        @apply flex flex-col;
        @apply gap-4;
      }

      .attachment-list_header {
        @apply flex items-center justify-between;
      }

      .attachment-list_title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .attachment-list_items {
        @apply flex flex-col;
        @apply gap-3;
      }

      .attachment-list_loading,
      .attachment-list_empty {
        @apply text-sm;
        @apply text-text-secondary;
        @apply text-center;
        @apply py-8;
      }

      .attachment-list_item {
        @apply flex items-center gap-4;
        @apply p-4;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .attachment-list_item-icon {
        @apply flex-shrink-0;
      }

      .attachment-list_item-thumbnail {
        @apply w-12 h-12;
        @apply rounded;
        @apply overflow-hidden;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-tertiary;
        @apply cursor-pointer;
        @apply transition-transform;
        @apply hover:scale-105;
      }

      .attachment-list_thumbnail-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .attachment-list_item-info {
        @apply flex-1;
        @apply flex flex-col;
        @apply gap-1;
      }

      .attachment-list_item-name {
        @apply font-medium;
        @apply text-text-primary;
      }

      .attachment-list_item-meta {
        @apply text-xs;
        @apply text-text-secondary;
      }

      .attachment-list_item-actions {
        @apply flex items-center gap-2;
      }

      .attachment-list_download-link {
        text-decoration: none;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AttachmentList {
  readonly attachmentService = inject(AttachmentService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  readonly issueId = input.required<string>();

  readonly attachments = computed(() => this.attachmentService.attachmentsList());

  private readonly initializeEffect = effect(
    () => {
      const issueId = this.issueId();
      if (issueId) {
        this.attachmentService.setIssue(issueId);
        this.attachmentService.loadAttachments();
      }
    },
    { allowSignalWrites: true },
  );

  getDownloadUrl(attachmentId: string): string {
    return this.attachmentService.getDownloadUrl(attachmentId);
  }

  formatFileSize(bytes: number): string {
    return this.attachmentService.formatFileSize(bytes);
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }

  async handleDeleteAttachment(attachment: Attachment): Promise<void> {
    if (
      !confirm(
        this.translateService.instant('attachments.deleteConfirm', {
          fileName: attachment.original_name,
        }),
      )
    ) {
      return;
    }

    try {
      await this.attachmentService.deleteAttachment(attachment.id);
    } catch (error) {
      console.error('Failed to delete attachment:', error);
    }
  }

  isImage(mimeType: string): boolean {
    return mimeType.startsWith('image/');
  }

  handlePreview(attachment: Attachment): void {
    this.modal.open(FilePreviewModal, this.viewContainerRef, {
      size: 'lg',
      data: { attachment },
    });
  }
}
