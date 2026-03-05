import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Label {
  id: string;
  project_id?: string;
  name: string;
  color: string;
  description?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ListProjectLabelsParams {
  page?: number;
  limit?: number;
  search?: string;
}

export interface ProjectLabelsResponse {
  labels: Label[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface CreateLabelRequest {
  name: string;
  color: string;
  description?: string;
}

export interface UpdateLabelRequest {
  name?: string;
  color?: string;
  description?: string;
}

type LabelsListPayload = ProjectLabelsResponse | Label[];

@Injectable({
  providedIn: 'root',
})
export class LabelService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  async listProjectLabels(
    projectId: string,
    params: ListProjectLabelsParams = {},
  ): Promise<ProjectLabelsResponse> {
    let httpParams = new HttpParams();

    if (params.page !== undefined) {
      httpParams = httpParams.set('page', params.page.toString());
    }
    if (params.limit !== undefined) {
      httpParams = httpParams.set('limit', params.limit.toString());
    }
    if (params.search?.trim()) {
      httpParams = httpParams.set('search', params.search.trim());
    }

    const response = await firstValueFrom(
      this.http.get<LabelsListPayload>(`${this.apiUrl}/projects/${projectId}/labels`, {
        params: httpParams,
      }),
    );

    if (Array.isArray(response)) {
      return {
        labels: response,
        total: response.length,
        page: params.page ?? 1,
        limit: params.limit ?? response.length,
        pages: 1,
      };
    }

    return response;
  }

  async createLabel(projectId: string, request: CreateLabelRequest): Promise<Label> {
    return await firstValueFrom(
      this.http.post<Label>(`${this.apiUrl}/projects/${projectId}/labels`, request),
    );
  }

  async updateLabel(labelId: string, request: UpdateLabelRequest): Promise<Label> {
    return await firstValueFrom(this.http.put<Label>(`${this.apiUrl}/labels/${labelId}`, request));
  }

  async deleteLabel(labelId: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/labels/${labelId}`));
  }

  async listIssueLabels(issueId: string): Promise<Label[]> {
    const response = await firstValueFrom(
      this.http.get<LabelsListPayload>(`${this.apiUrl}/issues/${issueId}/labels`),
    );
    return Array.isArray(response) ? response : response.labels || [];
  }

  async addIssueLabel(issueId: string, labelId: string): Promise<void> {
    await firstValueFrom(
      this.http.post(`${this.apiUrl}/issues/${issueId}/labels`, {
        label_id: labelId,
      }),
    );
  }

  async removeIssueLabel(issueId: string, labelId: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/issues/${issueId}/labels/${labelId}`));
  }
}
