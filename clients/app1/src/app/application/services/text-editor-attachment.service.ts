import { Injectable, inject } from '@angular/core';
import type { TextEditorAttachmentServiceInterface, AttachmentMetadata } from 'shared-ui';
import { NavigationService } from './navigation.service';
import { AttachmentApiService } from './attachment-api.service';
import { generateUUID } from '../utils/uuid.util';

/**
 * Implementation of TextEditorAttachmentServiceInterface for the text editor
 * Uses AttachmentApiService for HTTP calls and NavigationService for context
 */
@Injectable({
  providedIn: 'root',
})
export class TextEditorAttachmentService implements TextEditorAttachmentServiceInterface {
  private readonly attachmentApi = inject(AttachmentApiService);
  private readonly navigationService = inject(NavigationService);

  getNextId(): string {
    // Generate a UUID for temporary attachment IDs before upload
    // This will be replaced with the actual attachment ID after upload
    return generateUUID();
  }

  async upload(file: File): Promise<string> {
    const issueId = this.navigationService.currentIssueId();
    if (!issueId) {
      throw new Error(
        'Cannot upload attachment: No issue context available. Please open an issue first.',
      );
    }

    const response = await this.attachmentApi.uploadAttachment(issueId, file);
    return response.id;
  }

  async getAttachmentMetadata(id: string): Promise<AttachmentMetadata | null> {
    const response = await this.attachmentApi.getAttachmentMetadata(id);

    if (!response) {
      return null;
    }

    return {
      id: response.id,
      filename: response.original_name,
      mimeType: response.mime_type,
      fileSize: response.file_size,
      thumbnailUrl: response.thumbnail_path,
      previewUrl: response.download_url,
    };
  }

  async download(attachmentId: string): Promise<void> {
    // Try to get filename from download response first
    const { blob, filename: headerFilename } =
      await this.attachmentApi.downloadAttachment(attachmentId);

    // If filename wasn't in headers, try to get it from metadata
    let filename = headerFilename;
    if (filename === 'attachment') {
      const metadata = await this.getAttachmentMetadata(attachmentId);
      if (metadata?.filename) {
        filename = metadata.filename;
      }
    }

    // Create a temporary link and trigger download
    const link = document.createElement('a');
    const blobUrl = URL.createObjectURL(blob);
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up the blob URL after a short delay
    setTimeout(() => {
      URL.revokeObjectURL(blobUrl);
    }, 100);
  }

  async deleteAttachment(id: string): Promise<void> {
    await this.attachmentApi.deleteAttachment(id);
  }

  async canDeleteAttachment(id: string): Promise<boolean> {
    // For now, we assume the user can delete if they can access the attachment
    // The backend will handle actual permission checks
    const metadata = await this.getAttachmentMetadata(id);
    return metadata !== null;
  }
}
