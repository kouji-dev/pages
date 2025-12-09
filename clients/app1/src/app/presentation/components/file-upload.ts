import { Component, ChangeDetectionStrategy, computed, inject, input, signal } from '@angular/core';
import { Button, Icon } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { AttachmentService } from '../../application/services/attachment.service';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [Button, Icon],
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
            Drag and drop files here, or
            <button
              type="button"
              class="file-upload_dropzone-button"
              (click)="fileInput.click()"
              [disabled]="isUploading()"
            >
              browse
            </button>
          </p>
          <p class="file-upload_dropzone-hint">Maximum file size: 10MB</p>
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
              Upload {{ selectedFiles().length }} file{{ selectedFiles().length > 1 ? 's' : '' }}
            </lib-button>
            <lib-button
              variant="ghost"
              size="md"
              (clicked)="clearFiles()"
              [disabled]="isUploading()"
            >
              Clear
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
        @apply border-border-default;
        @apply rounded-lg;
        @apply p-8;
        @apply text-center;
        @apply bg-bg-secondary;
        @apply transition-colors;
        @apply cursor-pointer;
      }

      .file-upload_dropzone:hover {
        @apply border-primary-400;
        @apply bg-primary-50;
      }

      .file-upload_dropzone--dragover {
        @apply border-primary-500;
        @apply bg-primary-100;
      }

      .file-upload_dropzone-content {
        @apply flex flex-col;
        @apply items-center;
        @apply gap-2;
      }

      .file-upload_dropzone-text {
        @apply text-sm;
        @apply text-text-primary;
        margin: 0;
      }

      .file-upload_dropzone-button {
        @apply text-primary-600;
        @apply font-medium;
        @apply underline;
        @apply bg-transparent;
        @apply border-none;
        @apply cursor-pointer;
        @apply hover:text-primary-700;
      }

      .file-upload_dropzone-button:disabled {
        @apply opacity-50;
        @apply cursor-not-allowed;
      }

      .file-upload_dropzone-hint {
        @apply text-xs;
        @apply text-text-secondary;
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
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .file-upload_file-info {
        @apply flex items-center gap-2;
        @apply flex-1;
        @apply min-w-0;
      }

      .file-upload_file-name {
        @apply font-medium;
        @apply text-text-primary;
        @apply truncate;
        @apply flex-1;
      }

      .file-upload_file-size {
        @apply text-xs;
        @apply text-text-secondary;
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
        this.toast.error(`File "${file.name}" exceeds 10MB limit`);
        continue;
      }
      validFiles.push(file);
    }

    if (validFiles.length > 0) {
      this.selectedFiles.update((current) => [...current, ...validFiles]);
      if (validFiles.length < files.length) {
        this.toast.warning(
          `${files.length - validFiles.length} file(s) were skipped due to size limits`,
        );
      }
    }
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
          this.toast.error(`Failed to upload "${file.name}"`);
        }
      }

      const successCount = files.length;
      this.toast.success(`Successfully uploaded ${successCount} file(s)!`);
      this.selectedFiles.set([]);
    } catch (error) {
      console.error('Failed to upload files:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to upload files. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isUploading.set(false);
    }
  }
}
