import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface IssueActivity {
  id: string;
  issue_id: string;
  user_id?: string;
  user_name?: string;
  user_email?: string;
  action: string;
  field_name?: string;
  old_value?: string;
  new_value?: string;
  created_at: string;
}

export interface IssueActivityListResponse {
  activities: IssueActivity[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

@Injectable({
  providedIn: 'root',
})
export class IssueActivityService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/issues`;

  // Current issue ID signal
  private readonly currentIssueId = signal<string | null>(null);

  // Current page signal
  private readonly currentPage = signal<number>(1);
  private readonly pageLimit = 50;

  // Activities resource using httpResource with computed URL
  private readonly activitiesResource = httpResource<IssueActivityListResponse>(() => {
    const issueId = this.currentIssueId();
    if (!issueId) return undefined;

    const page = this.currentPage();
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', this.pageLimit.toString());

    return `${this.apiUrl}/${issueId}/activities?${params.toString()}`;
  });

  // Public accessors
  readonly activities = computed(() => {
    const value = this.activitiesResource.value();
    return value?.activities || [];
  });

  readonly totalActivities = computed(() => {
    const value = this.activitiesResource.value();
    return value?.total || 0;
  });

  readonly currentPageNumber = computed(() => {
    const value = this.activitiesResource.value();
    return value?.page || 1;
  });

  readonly totalPages = computed(() => {
    const value = this.activitiesResource.value();
    return value?.pages || 0;
  });

  readonly isLoading = computed(() => this.activitiesResource.isLoading());
  readonly error = computed(() => this.activitiesResource.error());
  readonly hasError = computed(() => this.activitiesResource.error() !== undefined);

  /**
   * Load activities for an issue
   */
  loadActivities(issueId: string, page: number = 1): void {
    this.currentIssueId.set(issueId);
    this.currentPage.set(page);
    // Resource will reload automatically when issueId or page changes
  }

  /**
   * Reload activities from API
   */
  reloadActivities(): void {
    this.activitiesResource.reload();
  }

  /**
   * Go to next page
   */
  nextPage(): void {
    const current = this.currentPageNumber();
    const total = this.totalPages();
    if (current < total) {
      this.currentPage.set(current + 1);
    }
  }

  /**
   * Go to previous page
   */
  previousPage(): void {
    const current = this.currentPageNumber();
    if (current > 1) {
      this.currentPage.set(current - 1);
    }
  }
}
