import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

const API_URL = environment.apiUrl;

/**
 * Response type for project member
 */
export interface ProjectMemberApiResponse {
  user_id: string;
  project_id: string;
  role: 'admin' | 'member' | 'viewer';
  user_name: string;
  user_email: string;
  avatar_url?: string;
  joined_at: string;
}

/**
 * Response type for project member list
 */
export interface ProjectMemberListApiResponse {
  members: ProjectMemberApiResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

/**
 * Service for handling project members API calls
 * Separates HTTP concerns from business logic
 */
@Injectable({
  providedIn: 'root',
})
export class ProjectMembersApiService {
  private readonly http = inject(HttpClient);

  /**
   * Search project members by query
   * @param projectId Project ID
   * @param query Search query (name or email)
   * @param limit Maximum number of results (default: 20)
   */
  async searchProjectMembers(
    projectId: string,
    query: string,
    limit: number = 20,
  ): Promise<ProjectMemberApiResponse[]> {
    const params = new HttpParams()
      .set('page', '1')
      .set('limit', limit.toString())
      .set('search', query);

    const response = await firstValueFrom(
      this.http.get<ProjectMemberListApiResponse>(`${API_URL}/projects/${projectId}/members`, {
        params,
      }),
    );

    return response?.members || [];
  }

  /**
   * Get project members (for backward compatibility)
   */
  async getProjectMembers(
    projectId: string,
    page: number = 1,
    limit: number = 20,
  ): Promise<ProjectMemberListApiResponse> {
    const params = new HttpParams().set('page', page.toString()).set('limit', limit.toString());

    const response = await firstValueFrom(
      this.http.get<ProjectMemberListApiResponse>(`${API_URL}/projects/${projectId}/members`, {
        params,
      }),
    );

    if (!response) {
      throw new Error('Failed to get project members: No response from server');
    }

    return response;
  }
}
