import { Injectable, inject, computed, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

const API_URL = environment.apiUrl;

export interface Attachment {
  id: string;
  entity_type: string;
  entity_id: string;
  file_name: string;
  original_name: string;
  file_size: number;
  mime_type: string;
  storage_path: string;
  storage_type: string;
  thumbnail_path?: string;
  uploaded_by?: string;
  uploader_name?: string;
  uploader_email?: string;
  download_url?: string;
  created_at: string;
  updated_at: string;
}

export interface AttachmentListResponse {
  attachments: Attachment[];
  total: number;
}

@Injectable({
  providedIn: 'root',
})
export class AttachmentService {
  private readonly http = inject(HttpClient);

  // Current issue ID for filtering attachments
  private readonly currentIssueId = signal<string | null>(null);

  // Attachments list resource using httpResource with computed URL
  private readonly attachmentsResource = httpResource<AttachmentListResponse>(() => {
    const issueId = this.currentIssueId();
    if (!issueId) return undefined;

    return `${API_URL}/issues/${issueId}/attachments`;
  });

  // Public accessors for attachments list
  readonly attachmentsList = computed(() => {
    const value = this.attachmentsResource.value();
    return value?.attachments || [];
  });

  readonly isLoading = computed(() => this.attachmentsResource.isLoading());
  readonly error = computed(() => this.attachmentsResource.error());
  readonly hasError = computed(() => this.attachmentsResource.error() !== undefined);

  /**
   * Set current issue ID and load attachments
   */
  setIssue(issueId: string): void {
    this.currentIssueId.set(issueId);
    // Resource will reload automatically when issueId changes
  }

  /**
   * Reload attachments from API
   */
  loadAttachments(): void {
    this.attachmentsResource.reload();
  }

  /**
   * Upload a file attachment
   */
  async uploadAttachment(issueId: string, file: File): Promise<Attachment> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await firstValueFrom(
      this.http.post<Attachment>(`${API_URL}/issues/${issueId}/attachments`, formData),
    );
    if (!response) {
      throw new Error('Failed to upload attachment: No response from server');
    }

    // Reload attachments to get updated list
    this.loadAttachments();

    return response;
  }

  /**
   * Download an attachment
   */
  getDownloadUrl(attachmentId: string): string {
    return `${API_URL}/attachments/${attachmentId}/download`;
  }

  /**
   * Delete an attachment
   */
  async deleteAttachment(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${API_URL}/attachments/${id}`));

    // Reload attachments to get updated list
    this.loadAttachments();
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }
}
