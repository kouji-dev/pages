import { Component, ChangeDetectionStrategy, computed, signal, effect } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { injectAttachmentService } from '../interfaces/attachment-service.interface';
import { BaseNodeComponent } from './base-node-component';
import { AttachmentNode } from '../nodes/attachment-node';

@Component({
  selector: 'lib-text-editor-attachment-decorator',
  imports: [Button, Icon],
  template: `
    <div class="te-attachment-decorator" [attr.data-attachment-id]="attachmentId()">
      @if (metadata(); as meta) {
        <div class="te-attachment-decorator_content">
          <div class="te-attachment-decorator_icon">
            <lib-icon name="file" size="sm" />
          </div>
          <div class="te-attachment-decorator_info">
            <div class="te-attachment-decorator_filename">{{ meta.filename }}</div>
            <div class="te-attachment-decorator_meta">
              {{ formatFileSize(meta.fileSize) }} • {{ meta.mimeType }}
            </div>
          </div>
          <div class="te-attachment-decorator_actions">
            <lib-button
              variant="ghost"
              size="sm"
              (clicked)="handleDownload()"
              leftIcon="download"
            />
            @if (canDelete()) {
              <lib-button
                variant="ghost"
                size="sm"
                (clicked)="handleDelete()"
                class="te-attachment-decorator_delete"
                leftIcon="x"
              />
            }
          </div>
        </div>
      } @else {
        <div class="te-attachment-decorator_loading">Loading attachment...</div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .te-attachment-decorator {
        @apply inline-block;
        @apply my-1;
        @apply max-w-xs;
        @apply w-full;
      }

      .te-attachment-decorator_content {
        @apply flex items-center gap-2;
        @apply p-2;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-muted;
        @apply transition-colors;
        @apply min-w-0;
      }

      .te-attachment-decorator_icon {
        @apply flex-shrink-0;
      }

      .te-attachment-decorator_info {
        @apply flex-1;
        @apply min-w-0;
        @apply overflow-hidden;
      }

      .te-attachment-decorator_filename {
        @apply font-medium;
        @apply text-foreground;
        @apply text-sm;
        @apply truncate;
      }

      .te-attachment-decorator_meta {
        @apply text-xs;
        @apply text-muted-foreground;
        @apply truncate;
      }

      .te-attachment-decorator_actions {
        @apply flex items-center gap-0.5;
        @apply flex-shrink-0;
      }

      .te-attachment-decorator_loading {
        @apply text-xs;
        @apply text-muted-foreground;
        @apply italic;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AttachmentDecoratorComponent extends BaseNodeComponent<AttachmentNode> {
  private readonly attachmentService = injectAttachmentService();

  readonly attachmentId = computed(() => {
    const node = this.currentNode();
    return node ? node.getAttachmentId() : '';
  });

  readonly metadata = signal<any>(null);
  readonly canDelete = signal<boolean>(false);

  constructor() {
    super();
    // Load metadata when node changes
    effect(() => {
      const node = this.currentNode();
      if (node) {
        const id = node.getAttachmentId();
        this.attachmentService.getAttachmentMetadata(id).then((meta) => {
          this.metadata.set(meta);
          this.attachmentService.canDeleteAttachment(id).then((canDelete) => {
            this.canDelete.set(canDelete);
          });
        });
      } else {
        this.metadata.set(null);
        this.canDelete.set(false);
      }
    });
  }

  async handleDownload(): Promise<void> {
    try {
      await this.attachmentService.download(this.attachmentId());
    } catch (error) {
      console.error('Failed to download attachment:', error);
    }
  }

  async handleDelete(): Promise<void> {
    if (this.canDelete()) {
      try {
        await this.attachmentService.deleteAttachment(this.attachmentId());
      } catch (error) {
        console.error('Failed to delete attachment:', error);
      }
    }
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }
}
