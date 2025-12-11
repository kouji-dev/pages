import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

const API_URL = environment.apiUrl;

/**
 * Response type for attachment upload
 */
export interface UploadAttachmentResponse {
  id: string;
  file_name: string;
  original_name: string;
  file_size: number;
  mime_type: string;
  thumbnail_path?: string;
  download_url?: string;
}

/**
 * Response type for attachment metadata
 */
export interface AttachmentMetadataResponse {
  id: string;
  file_name: string;
  original_name: string;
  file_size: number;
  mime_type: string;
  thumbnail_path?: string;
  download_url?: string;
}

/**
 * Service for handling attachment API calls
 * Separates HTTP concerns from business logic
 */
@Injectable({
  providedIn: 'root',
})
export class AttachmentApiService {
  private readonly http = inject(HttpClient);

  /**
   * Upload a file attachment to an issue
   */
  async uploadAttachment(issueId: string, file: File): Promise<UploadAttachmentResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await firstValueFrom(
      this.http.post<UploadAttachmentResponse>(
        `${API_URL}/issues/${issueId}/attachments`,
        formData,
      ),
    );

    if (!response || !response.id) {
      throw new Error('Failed to upload attachment: No response from server');
    }

    return response;
  }

  /**
   * Get attachment metadata by ID
   */
  async getAttachmentMetadata(id: string): Promise<AttachmentMetadataResponse | null> {
    try {
      const response = await firstValueFrom(
        this.http.get<AttachmentMetadataResponse>(`${API_URL}/attachments/${id}`),
      );
      return response || null;
    } catch (error) {
      console.error('Failed to get attachment metadata:', error);
      return null;
    }
  }

  /**
   * Download an attachment file
   * Returns the blob and filename
   */
  async downloadAttachment(attachmentId: string): Promise<{ blob: Blob; filename: string }> {
    const url = `${API_URL}/attachments/${attachmentId}/download`;

    // Fetch the file as a blob and observe the full response to get headers
    const response = await firstValueFrom(
      this.http.get(url, { responseType: 'blob', observe: 'response' }),
    );

    if (!response.body) {
      throw new Error('Failed to download attachment: No file content received');
    }

    // Try to get filename from Content-Disposition header
    let filename = 'attachment';
    const contentDisposition = response.headers.get('Content-Disposition');
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }

    return { blob: response.body, filename };
  }

  /**
   * Delete an attachment
   */
  async deleteAttachment(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${API_URL}/attachments/${id}`));
  }
}
