import { Injectable, inject, computed, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

const API_URL = environment.apiUrl;

export interface Comment {
  id: string;
  entity_type: string;
  entity_id: string;
  issue_id?: string;
  page_id?: string;
  user_id: string;
  content: string;
  is_edited: boolean;
  user_name: string;
  user_email: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface CommentListResponse {
  comments: Comment[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface CreateCommentRequest {
  content: string;
}

export interface UpdateCommentRequest {
  content: string;
}

@Injectable({
  providedIn: 'root',
})
export class CommentService {
  private readonly http = inject(HttpClient);

  // Current issue ID for filtering comments
  private readonly currentIssueId = signal<string | null>(null);
  // Current page ID for filtering comments
  private readonly currentPageId = signal<string | null>(null);
  // Entity type: 'issue' or 'page'
  private readonly entityType = signal<'issue' | 'page' | null>(null);

  // Comments list resource using httpResource with computed URL
  private readonly commentsResource = httpResource<CommentListResponse>(() => {
    const issueId = this.currentIssueId();
    const pageId = this.currentPageId();
    const type = this.entityType();

    if (!type) return undefined;

    const entityId = type === 'issue' ? issueId : pageId;
    if (!entityId) return undefined;

    const page = this.currentPage();
    const limit = 50; // Default limit

    const params = new HttpParams().set('page', page.toString()).set('limit', limit.toString());

    const endpoint =
      type === 'issue'
        ? `${API_URL}/issues/${entityId}/comments`
        : `${API_URL}/pages/${entityId}/comments`;

    return `${endpoint}?${params.toString()}`;
  });

  // Current page signal
  private readonly page = signal<number>(1);

  readonly currentPage = computed(() => this.page());

  // Public accessors for comments list
  readonly commentsList = computed(() => {
    const value = this.commentsResource.value();
    return value?.comments || [];
  });

  readonly commentsTotal = computed(() => {
    const value = this.commentsResource.value();
    return value?.total || 0;
  });

  readonly isLoading = computed(() => this.commentsResource.isLoading());
  readonly error = computed(() => this.commentsResource.error());
  readonly hasError = computed(() => this.commentsResource.error() !== undefined);

  /**
   * Set current issue ID and load comments
   */
  setIssue(issueId: string): void {
    this.currentIssueId.set(issueId);
    this.currentPageId.set(null);
    this.entityType.set('issue');
    this.page.set(1);
    // Resource will reload automatically when issueId changes
  }

  /**
   * Set current page ID and load comments
   */
  setPage(pageId: string): void {
    this.currentPageId.set(pageId);
    this.currentIssueId.set(null);
    this.entityType.set('page');
    this.page.set(1);
    // Resource will reload automatically when pageId changes
  }

  /**
   * Reload comments from API
   */
  loadComments(): void {
    this.commentsResource.reload();
  }

  /**
   * Create a new comment for an issue
   */
  async createComment(issueId: string, request: CreateCommentRequest): Promise<Comment> {
    const response = await firstValueFrom(
      this.http.post<Comment>(`${API_URL}/issues/${issueId}/comments`, request),
    );
    if (!response) {
      throw new Error('Failed to create comment: No response from server');
    }

    // Reload comments to get updated list
    this.loadComments();

    return response;
  }

  /**
   * Create a new comment for a page
   */
  async createPageComment(pageId: string, request: CreateCommentRequest): Promise<Comment> {
    const response = await firstValueFrom(
      this.http.post<Comment>(`${API_URL}/pages/${pageId}/comments`, request),
    );
    if (!response) {
      throw new Error('Failed to create comment: No response from server');
    }

    // Reload comments to get updated list
    this.loadComments();

    return response;
  }

  /**
   * Update a comment
   */
  async updateComment(id: string, request: UpdateCommentRequest): Promise<Comment> {
    const response = await firstValueFrom(
      this.http.put<Comment>(`${API_URL}/comments/${id}`, request),
    );
    if (!response) {
      throw new Error('Failed to update comment: No response from server');
    }

    // Reload comments to get updated list
    this.loadComments();

    return response;
  }

  /**
   * Delete a comment
   */
  async deleteComment(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${API_URL}/comments/${id}`));

    // Reload comments to get updated list
    this.loadComments();
  }
}
