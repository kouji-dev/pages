import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';

export interface IssueUser {
  id: string;
  name: string;
  avatar_url?: string | null;
}

export interface Issue {
  id: string;
  project_id: string;
  issue_number: number;
  key: string;
  title: string;
  description?: string;
  type: 'task' | 'bug' | 'story' | 'epic';
  status: 'todo' | 'in_progress' | 'done' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  reporter_id?: string;
  assignee_id?: string;
  reporter?: IssueUser | null;
  assignee?: IssueUser | null;
  due_date?: string;
  story_points?: number;
  created_at: string;
  updated_at: string;
}

export interface IssueListItem {
  id: string;
  project_id: string;
  issue_number: number;
  key: string;
  title: string;
  type: 'task' | 'bug' | 'story' | 'epic';
  status: 'todo' | 'in_progress' | 'done' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee_id?: string;
  reporter_id?: string;
  due_date?: string;
  created_at: string;
  updated_at: string;
}

export interface IssueListResponse {
  issues: IssueListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface CreateIssueRequest {
  project_id: string;
  title: string;
  description?: string;
  type?: 'task' | 'bug' | 'story' | 'epic';
  status?: 'todo' | 'in_progress' | 'done' | 'cancelled';
  priority?: 'low' | 'medium' | 'high' | 'critical';
  assignee_id?: string;
  due_date?: string;
  story_points?: number;
}

export interface UpdateIssueRequest {
  title?: string;
  description?: string;
  type?: 'task' | 'bug' | 'story' | 'epic';
  status?: 'todo' | 'in_progress' | 'done' | 'cancelled';
  priority?: 'low' | 'medium' | 'high' | 'critical';
  assignee_id?: string;
  due_date?: string;
  story_points?: number;
}

export interface ListIssuesFilters {
  project_id: string;
  page?: number;
  limit?: number;
  search?: string;
  assignee_id?: string;
  reporter_id?: string;
  status?: 'todo' | 'in_progress' | 'done' | 'cancelled';
  type?: 'task' | 'bug' | 'story' | 'epic';
  priority?: 'low' | 'medium' | 'high' | 'critical';
  sort_by?: 'created_at' | 'title' | 'type' | 'status' | 'priority' | 'updated_at';
  sort_order?: 'asc' | 'desc';
}

@Injectable({
  providedIn: 'root',
})
export class IssueService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/issues`;
  private readonly navigationService = inject(NavigationService);

  // Note: projectId and issueId are now URL-driven via NavigationService
  // No need for internal signals

  // Issues list resource using httpResource - driven by URL organizationId and projectId
  private readonly issuesResource = httpResource<IssueListResponse>(() => {
    const organizationId = this.navigationService.currentOrganizationId();
    const projectId = this.navigationService.currentProjectId();
    if (!organizationId || !projectId) return undefined;

    const filters = this.currentFilters();
    let params = new HttpParams()
      .set('organization_id', organizationId)
      .set('project_id', projectId)
      .set('page', filters.page?.toString() || '1')
      .set('limit', filters.limit?.toString() || '20');

    if (filters.search) {
      params = params.set('search', filters.search);
    }
    if (filters.assignee_id) {
      params = params.set('assignee_id', filters.assignee_id);
    }
    if (filters.reporter_id) {
      params = params.set('reporter_id', filters.reporter_id);
    }
    if (filters.status) {
      params = params.set('status', filters.status);
    }
    if (filters.type) {
      params = params.set('type', filters.type);
    }
    if (filters.priority) {
      params = params.set('priority', filters.priority);
    }
    if (filters.sort_by) {
      params = params.set('sort_by', filters.sort_by);
    }
    if (filters.sort_order) {
      params = params.set('sort_order', filters.sort_order);
    }

    return `${this.apiUrl}?${params.toString()}`;
  });

  // Current filters signal
  private readonly filters = signal<Omit<ListIssuesFilters, 'project_id'>>({
    page: 1,
    limit: 20,
  });

  readonly currentFilters = computed(() => this.filters());

  // Optimistic updates state
  private readonly optimisticIssues = signal<Map<string, IssueListItem>>(new Map());
  private readonly optimisticIssueIds = signal<Set<string>>(new Set()); // IDs to add optimistically
  private readonly deletedIssueIds = signal<Set<string>>(new Set()); // IDs deleted optimistically

  // Public accessors for issues list (merged with optimistic updates)
  readonly issuesList = computed(() => {
    const value = this.issuesResource.value();
    const baseIssues = value?.issues || [];
    const optimisticMap = this.optimisticIssues();
    const optimisticIds = this.optimisticIssueIds();
    const deletedIds = this.deletedIssueIds();

    // Start with base issues, excluding deleted ones
    let issues = baseIssues.filter((issue) => !deletedIds.has(issue.id));

    // Add optimistic issues that aren't in base list
    optimisticIds.forEach((id) => {
      if (!issues.find((issue) => issue.id === id)) {
        const optimisticIssue = optimisticMap.get(id);
        if (optimisticIssue) {
          issues.push(optimisticIssue);
        }
      }
    });

    // Update existing issues with optimistic changes
    issues = issues.map((issue) => {
      const optimisticIssue = optimisticMap.get(issue.id);
      return optimisticIssue || issue;
    });

    return issues;
  });

  readonly issuesTotal = computed(() => {
    const value = this.issuesResource.value();
    return value?.total || 0;
  });

  readonly issuesPage = computed(() => {
    const value = this.issuesResource.value();
    return value?.page || 1;
  });

  readonly issuesPages = computed(() => {
    const value = this.issuesResource.value();
    return value?.pages || 0;
  });

  readonly isLoading = computed(() => this.issuesResource.isLoading());
  readonly error = computed(() => this.issuesResource.error());
  readonly hasError = computed(() => this.issuesResource.error() !== undefined);

  // Single issue resource using httpResource - driven by URL issueId
  private readonly issueResource = httpResource<Issue>(() => {
    const id = this.navigationService.currentIssueId();
    return id ? `${this.apiUrl}/${id}` : undefined;
  });

  // Current issue computed from resource
  readonly currentIssue = computed(() => {
    return this.issueResource.value() as Issue | undefined;
  });

  readonly isFetchingIssue = computed(() => this.issueResource.isLoading());
  readonly issueError = computed(() => this.issueResource.error());
  readonly hasIssueError = computed(() => this.issueResource.error() !== undefined);

  /**
   * Set current project ID and load issues
   * @deprecated Project ID is now URL-driven via NavigationService
   */
  setProject(projectId: string): void {
    // Project ID is now URL-driven
    // This method is kept for backward compatibility
  }

  /**
   * Set filters and reload issues
   */
  setFilters(filters: Partial<Omit<ListIssuesFilters, 'project_id'>>): void {
    this.filters.update((current) => ({ ...current, ...filters }));
    // Resource will reload automatically when filters change
  }

  /**
   * Reload issues from API
   */
  loadIssues(): void {
    this.issuesResource.reload();
  }

  /**
   * Fetch a single issue by ID using httpResource
   * @deprecated Issue ID is now driven by URL via NavigationService
   * The issue will be automatically fetched when URL issueId changes
   */
  fetchIssue(id: string): void {
    // Issue fetching is now URL-driven via navigationService.currentIssueId()
    // This method is kept for backward compatibility
  }

  /**
   * Get current issue signal
   */
  getCurrentIssue(): typeof this.currentIssue {
    return this.currentIssue;
  }

  /**
   * Get issues list signal
   */
  getIssues(): typeof this.issuesList {
    return this.issuesList;
  }

  /**
   * Create a new issue with optimistic update
   */
  async createIssue(request: CreateIssueRequest): Promise<Issue> {
    // Create optimistic issue item
    const optimisticId = `temp-${Date.now()}`;
    const optimisticIssue: IssueListItem = {
      id: optimisticId,
      project_id: request.project_id,
      issue_number: 0, // Temporary, will be replaced by real data
      key: 'TEMP',
      title: request.title,
      type: request.type || 'task',
      status: request.status || 'todo',
      priority: request.priority || 'medium',
      assignee_id: request.assignee_id,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Add optimistically
    this.optimisticIssues.update((map) => {
      const newMap = new Map(map);
      newMap.set(optimisticId, optimisticIssue);
      return newMap;
    });
    this.optimisticIssueIds.update((set) => new Set(set).add(optimisticId));

    try {
      const response = await firstValueFrom(this.http.post<Issue>(this.apiUrl, request));
      if (!response) {
        throw new Error('Failed to create issue: No response from server');
      }

      // Remove optimistic entry
      this.optimisticIssues.update((map) => {
        const newMap = new Map(map);
        newMap.delete(optimisticId);
        return newMap;
      });
      this.optimisticIssueIds.update((set) => {
        const newSet = new Set(set);
        newSet.delete(optimisticId);
        return newSet;
      });

      // Reload issues to get updated list with real data
      this.loadIssues();

      return response;
    } catch (error) {
      // Revert optimistic update on error
      this.optimisticIssues.update((map) => {
        const newMap = new Map(map);
        newMap.delete(optimisticId);
        return newMap;
      });
      this.optimisticIssueIds.update((set) => {
        const newSet = new Set(set);
        newSet.delete(optimisticId);
        return newSet;
      });
      throw error;
    }
  }

  /**
   * Update an issue with optimistic update
   */
  async updateIssue(id: string, updates: UpdateIssueRequest): Promise<Issue> {
    // Get current issue from list or resource
    const currentIssues = this.issuesResource.value()?.issues || [];
    const currentIssue = currentIssues.find((issue) => issue.id === id);
    const currentIssueDetail = this.issueResource.value() as Issue | undefined;

    // Create optimistic update
    if (currentIssue) {
      const optimisticIssue: IssueListItem = {
        ...currentIssue,
        title: updates.title ?? currentIssue.title,
        type: updates.type ?? currentIssue.type,
        status: updates.status ?? currentIssue.status,
        priority: updates.priority ?? currentIssue.priority,
        assignee_id:
          updates.assignee_id !== undefined ? updates.assignee_id : currentIssue.assignee_id,
      };

      this.optimisticIssues.update((map) => {
        const newMap = new Map(map);
        newMap.set(id, optimisticIssue);
        return newMap;
      });
    }

    try {
      const response = await firstValueFrom(this.http.put<Issue>(`${this.apiUrl}/${id}`, updates));
      if (!response) {
        throw new Error('Failed to update issue: No response from server');
      }

      // Remove optimistic update
      this.optimisticIssues.update((map) => {
        const newMap = new Map(map);
        newMap.delete(id);
        return newMap;
      });

      // Reload issues list and current issue to get updated data
      this.loadIssues();
      const currentIssueId = this.navigationService.currentIssueId();
      if (currentIssueId === id) {
        this.issueResource.reload();
      }

      return response;
    } catch (error) {
      // Revert optimistic update on error
      this.optimisticIssues.update((map) => {
        const newMap = new Map(map);
        newMap.delete(id);
        return newMap;
      });
      throw error;
    }
  }

  /**
   * Delete an issue with optimistic update
   */
  async deleteIssue(id: string): Promise<void> {
    // Mark as deleted optimistically
    this.deletedIssueIds.update((set) => new Set(set).add(id));

    try {
      await firstValueFrom(this.http.delete(`${this.apiUrl}/${id}`));

      // Remove from deleted set (reload will handle it)
      this.deletedIssueIds.update((set) => {
        const newSet = new Set(set);
        newSet.delete(id);
        return newSet;
      });

      // Reload issues to get updated list
      this.loadIssues();

      // If deleted issue was current, navigation will handle clearing it
      // (user will be redirected or URL will change)
    } catch (error) {
      // Revert optimistic delete on error
      this.deletedIssueIds.update((set) => {
        const newSet = new Set(set);
        newSet.delete(id);
        return newSet;
      });
      throw error;
    }
  }
}
