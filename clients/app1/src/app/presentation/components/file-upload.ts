import { Component, ChangeDetectionStrategy, computed, inject, input, signal } from '@angular/core';
import { Button } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { AttachmentService } from '../../application/services/attachment.service';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [Button],
  template: `
    <div class="file-upload">
      <input
        type="file"
        #fileInput
        (change)="handleFileSelect($event)"
        class="file-upload_input"
        [multiple]="false"
      />
      <lib-button
        variant="secondary"
        size="md"
        (clicked)="fileInput.click()"
        [loading]="isUploading()"
        [disabled]="isUploading()"
      >
        Upload File
      </lib-button>
      @if (selectedFile()) {
        <div class="file-upload_selected">
          <span>{{ selectedFile()!.name }}</span>
          <lib-button
            variant="ghost"
            size="sm"
            (clicked)="handleUpload()"
            [loading]="isUploading()"
          >
            Upload
          </lib-button>
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

      .file-upload_selected {
        @apply flex items-center justify-between;
        @apply p-3;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FileUpload {
  private readonly attachmentService = inject(AttachmentService);
  private readonly toast = inject(ToastService);

  readonly issueId = input.required<string>();

  readonly selectedFile = signal<File | null>(null);
  readonly isUploading = signal(false);

  handleFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        this.toast.error('File size must be less than 10MB');
        return;
      }
      this.selectedFile.set(file);
    }
  }

  async handleUpload(): Promise<void> {
    const file = this.selectedFile();
    if (!file) {
      return;
    }

    this.isUploading.set(true);

    try {
      await this.attachmentService.uploadAttachment(this.issueId(), file);
      this.toast.success('File uploaded successfully!');
      this.selectedFile.set(null);
    } catch (error) {
      console.error('Failed to upload file:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to upload file. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isUploading.set(false);
    }
  }
}
