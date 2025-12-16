import { Component, ChangeDetectionStrategy, computed, inject, input, signal } from '@angular/core';
import { Button, Icon } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { AttachmentService } from '../../../../application/services/attachment.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [Button, Icon, TranslatePipe],
  template: `
    <div class="file-upload">
      <input
        type="file"
        #fileInput
        (change)="handleFileSelect($event)"
        class="file-upload_input"
        [multiple]="true"
        [accept]="acceptedTypes()"
      />
      <div
        class="file-upload_dropzone"
        [class.file-upload_dropzone--dragover]="isDragOver()"
        (dragover)="handleDragOver($event)"
        (dragleave)="handleDragLeave($event)"
        (drop)="handleDrop($event)"
      >
        <div class="file-upload_dropzone-content">
          <lib-icon name="upload" size="lg" />
          <p class="file-upload_dropzone-text">
            {{ 'attachments.dragAndDrop' | translate }}
            <button
              type="button"
              class="file-upload_dropzone-button"
              (click)="fileInput.click()"
              [disabled]="isUploading()"
            >
              {{ 'attachments.browse' | translate }}
            </button>
          </p>
          <p class="file-upload_dropzone-hint">{{ 'attachments.maxFileSize' | translate }}</p>
        </div>
      </div>
      @if (selectedFiles().length > 0) {
        <div class="file-upload_files">
          @for (file of selectedFiles(); track file.name + file.size) {
            <div class="file-upload_file">
              <div class="file-upload_file-info">
                <lib-icon name="file" size="sm" />
                <span class="file-upload_file-name">{{ file.name }}</span>
                <span class="file-upload_file-size">{{ formatFileSize(file.size) }}</span>
              </div>
              <lib-button
                variant="ghost"
                size="sm"
                (clicked)="removeFile(file)"
                [disabled]="isUploading()"
              >
                <lib-icon name="x" size="sm" />
              </lib-button>
            </div>
          }
          <div class="file-upload_actions">
            <lib-button
              variant="primary"
              size="md"
              (clicked)="handleUploadAll()"
              [loading]="isUploading()"
              [disabled]="selectedFiles().length === 0"
            >
              {{ getUploadButtonLabel() }}
            </lib-button>
            <lib-button
              variant="ghost"
              size="md"
              (clicked)="clearFiles()"
              [disabled]="isUploading()"
            >
              {{ 'attachments.clear' | translate }}
            </lib-button>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .file-upload {
        @apply flex flex-col;
        @apply gap-3;
      }

      .file-upload_input {
        @apply hidden;
      }

      .file-upload_dropzone {
        @apply border-2;
        @apply border-dashed;
        @apply border-border;
        @apply rounded-lg;
        @apply p-8;
        @apply text-center;
        @apply bg-muted;
        @apply transition-colors;
        @apply cursor-pointer;
      }

      .file-upload_dropzone:hover {
        @apply border-primary;
        @apply bg-primary/10;
      }

      .file-upload_dropzone--dragover {
        @apply border-primary;
        @apply bg-primary/20;
      }

      .file-upload_dropzone-content {
        @apply flex flex-col;
        @apply items-center;
        @apply gap-2;
      }

      .file-upload_dropzone-text {
        @apply text-sm;
        @apply text-foreground;
        margin: 0;
      }

      .file-upload_dropzone-button {
        @apply text-primary;
        @apply font-medium;
        @apply underline;
        @apply bg-transparent;
        @apply border-none;
        @apply cursor-pointer;
        @apply hover:text-primary/80;
      }

      .file-upload_dropzone-button:disabled {
        @apply opacity-50;
        @apply cursor-not-allowed;
      }

      .file-upload_dropzone-hint {
        @apply text-xs;
        @apply text-muted-foreground;
        margin: 0;
      }

      .file-upload_files {
        @apply flex flex-col;
        @apply gap-2;
      }

      .file-upload_file {
        @apply flex items-center justify-between;
        @apply p-3;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-muted;
      }

      .file-upload_file-info {
        @apply flex items-center gap-2;
        @apply flex-1;
        @apply min-w-0;
      }

      .file-upload_file-name {
        @apply font-medium;
        @apply text-foreground;
        @apply truncate;
        @apply flex-1;
      }

      .file-upload_file-size {
        @apply text-xs;
        @apply text-muted-foreground;
        @apply flex-shrink-0;
      }

      .file-upload_actions {
        @apply flex items-center gap-2;
        @apply justify-end;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FileUpload {
  private readonly attachmentService = inject(AttachmentService);
  private readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);

  readonly issueId = input.required<string>();
  readonly acceptedTypes = input<string>('*/*'); // Accept all file types by default

  readonly selectedFiles = signal<File[]>([]);
  readonly isUploading = signal(false);
  readonly isDragOver = signal(false);

  handleFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files || []);
    this.addFiles(files);
    // Reset input so same file can be selected again
    input.value = '';
  }

  handleDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(true);
  }

  handleDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(false);
  }

  handleDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(false);

    const files = Array.from(event.dataTransfer?.files || []);
    this.addFiles(files);
  }

  private addFiles(files: File[]): void {
    const validFiles: File[] = [];
    const maxSize = 10 * 1024 * 1024; // 10MB

    for (const file of files) {
      if (file.size > maxSize) {
        this.toast.error(
          this.translateService.instant('attachments.fileExceedsLimit', { fileName: file.name }),
        );
        continue;
      }
      validFiles.push(file);
    }

    if (validFiles.length > 0) {
      this.selectedFiles.update((current) => [...current, ...validFiles]);
      if (validFiles.length < files.length) {
        this.toast.warning(
          this.translateService.instant('attachments.filesSkipped', {
            count: files.length - validFiles.length,
          }),
        );
      }
    }
  }

  getUploadButtonLabel(): string {
    const count = this.selectedFiles().length;
    return count === 1
      ? this.translateService.instant('attachments.uploadFile')
      : this.translateService.instant('attachments.uploadFiles', { count });
  }

  removeFile(file: File): void {
    this.selectedFiles.update((files) => files.filter((f) => f !== file));
  }

  clearFiles(): void {
    this.selectedFiles.set([]);
  }

  formatFileSize(bytes: number): string {
    return this.attachmentService.formatFileSize(bytes);
  }

  async handleUploadAll(): Promise<void> {
    const files = this.selectedFiles();
    if (files.length === 0) {
      return;
    }

    this.isUploading.set(true);

    try {
      // Upload files sequentially to avoid overwhelming the server
      for (const file of files) {
        try {
          await this.attachmentService.uploadAttachment(this.issueId(), file);
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
          this.toast.error(
            this.translateService.instant('attachments.uploadFileError', { fileName: file.name }),
          );
        }
      }

      const successCount = files.length;
      this.toast.success(
        this.translateService.instant('attachments.uploadSuccess', { count: successCount }),
      );
      this.selectedFiles.set([]);
    } catch (error) {
      console.error('Failed to upload files:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('attachments.uploadFilesError');
      this.toast.error(errorMessage);
    } finally {
      this.isUploading.set(false);
    }
  }
}
