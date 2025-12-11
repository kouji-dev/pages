import { InjectionToken, Type, inject, type Provider } from '@angular/core';

/**
 * Interface for handling attachments in the text editor
 */
export interface TextEditorAttachmentServiceInterface {
  /**
   * Get the next attachment ID to use
   * @returns Next unique attachment ID
   */
  getNextId(): string;

  /**
   * Upload a file and return the attachment ID
   * @param file The file to upload
   * @returns Promise that resolves with the attachment ID
   */
  upload(file: File): Promise<string>;

  /**
   * Get attachment metadata by ID
   * @param id Attachment ID
   * @returns Attachment metadata or null if not found
   */
  getAttachmentMetadata(id: string): Promise<AttachmentMetadata | null>;

  /**
   * Download an attachment
   * @param attachmentId Attachment ID
   * @returns Promise that resolves when download is initiated
   */
  download(attachmentId: string): Promise<void>;

  /**
   * Delete an attachment
   * @param id Attachment ID
   * @returns Promise that resolves when deletion is complete
   */
  deleteAttachment(id: string): Promise<void>;

  /**
   * Check if attachment can be deleted
   * @param id Attachment ID
   * @returns True if attachment can be deleted
   */
  canDeleteAttachment(id: string): Promise<boolean>;
}

/**
 * Metadata for an attachment
 */
export interface AttachmentMetadata {
  /** Attachment ID */
  id: string;
  /** Original filename */
  filename: string;
  /** MIME type */
  mimeType: string;
  /** File size in bytes */
  fileSize: number;
  /** Optional thumbnail URL for images */
  thumbnailUrl?: string;
  /** Optional preview URL */
  previewUrl?: string;
}

/**
 * Injection token for the attachment service
 * @internal - Use provideAttachmentService() and injectAttachmentService() instead
 */
const ATTACHMENT_SERVICE_TOKEN = new InjectionToken<TextEditorAttachmentServiceInterface>(
  'ATTACHMENT_SERVICE',
);

/**
 * Provides the attachment service for the text editor
 * @param service The attachment service implementation
 * @returns Provider for the attachment service
 */
export function provideAttachmentService(
  service: Type<TextEditorAttachmentServiceInterface>,
): Provider {
  return {
    provide: ATTACHMENT_SERVICE_TOKEN,
    useClass: service,
  };
}

/**
 * Injects the attachment service
 * @returns The attachment service (throws if not provided)
 */
export function injectAttachmentService(): TextEditorAttachmentServiceInterface {
  return inject(ATTACHMENT_SERVICE_TOKEN);
}
