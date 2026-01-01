import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';

export interface Sprint {
  id: string;
  name: string;
  goal?: string;
  startDate: Date | string;
  endDate: Date | string;
  status: 'planned' | 'active' | 'completed';
  totalIssues: number;
  completedIssues: number;
  projectId: string;
}

export interface SprintIssue {
  id: string;
  title: string;
  projectId: string;
  sprintId?: string;
  labels?: { name: string; color: string }[];
  priority?: 'high' | 'medium' | 'low';
  status: 'todo' | 'in_progress' | 'code_review' | 'done';
  storyPoints?: number;
  hasImage?: boolean;
  imageUrl?: string;
  assignee?: { name: string; avatar: string };
  type?: 'task' | 'bug' | 'link' | 'story';
}

export interface BurndownDataPoint {
  day: string;
  ideal: number;
  actual: number;
}

export interface CreateSprintRequest {
  name: string;
  goal?: string;
  startDate: string;
  endDate: string;
  projectId: string;
}

export interface UpdateSprintRequest {
  name?: string;
  goal?: string;
  startDate?: string;
  endDate?: string;
  status?: 'planned' | 'active' | 'completed';
}

export interface SprintResponse {
  id: string;
  name: string;
  goal?: string;
  start_date: string;
  end_date: string;
  status: 'planned' | 'active' | 'completed';
  total_issues: number;
  completed_issues: number;
  project_id: string;
  created_at: string;
  updated_at: string;
}

export interface SprintListResponse {
  sprints: SprintResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

@Injectable({
  providedIn: 'root',
})
export class SprintService {
  private readonly http = inject(HttpClient);
  private readonly navigationService = inject(NavigationService);
  private readonly apiUrl = `${environment.apiUrl}`;

  // Sprints list resource - driven by URL projectId
  readonly sprints = httpResource<SprintListResponse>(() => {
    const projectId = this.navigationService.currentProjectId();
    if (!projectId) return undefined;

    // Backend endpoint: /api/v1/projects/{project_id}/sprints
    return `${this.apiUrl}/projects/${projectId}/sprints`;
  });

  // Public accessors
  readonly sprintsList = computed(() => {
    const value = this.sprints.value();
    if (!value) return [];
    if (Array.isArray(value)) {
      return value.map((s) => this.mapToSprint(s));
    }
    return (value.sprints || []).map((s) => this.mapToSprint(s));
  });

  readonly isLoading = computed(() => this.sprints.isLoading());
  readonly hasError = computed(() => this.sprints.error() !== undefined);
  readonly error = computed(() => this.sprints.error());

  // Selected sprint signal (can be manually set)
  private readonly selectedSprintId = signal<string | null>(null);

  // Current sprint (manually selected, or active, or first planned)
  readonly currentSprint = computed(() => {
    const sprints = this.sprintsList();
    const selectedId = this.selectedSprintId();

    if (selectedId) {
      const selected = sprints.find((s) => s.id === selectedId);
      if (selected) return selected;
    }

    return (
      sprints.find((s) => s.status === 'active') ||
      sprints.find((s) => s.status === 'planned') ||
      null
    );
  });

  /**
   * Set the selected sprint
   */
  selectSprint(sprint: Sprint | null): void {
    this.selectedSprintId.set(sprint?.id || null);
  }

  /**
   * Map API response to Sprint model
   */
  private mapToSprint(response: SprintResponse): Sprint {
    return {
      id: response.id,
      name: response.name,
      goal: response.goal,
      startDate: response.start_date,
      endDate: response.end_date,
      status: response.status,
      totalIssues: response.total_issues,
      completedIssues: response.completed_issues,
      projectId: response.project_id,
    };
  }

  /**
   * Create a new sprint
   */
  async createSprint(request: CreateSprintRequest): Promise<Sprint> {
    const response = await firstValueFrom(
      this.http.post<SprintResponse>(`${this.apiUrl}/projects/${request.projectId}/sprints`, {
        name: request.name,
        goal: request.goal,
        start_date: request.startDate,
        end_date: request.endDate,
      }),
    );
    this.sprints.reload();
    return this.mapToSprint(response);
  }

  /**
   * Update a sprint
   */
  async updateSprint(id: string, request: UpdateSprintRequest): Promise<Sprint> {
    const response = await firstValueFrom(
      this.http.put<SprintResponse>(`${this.apiUrl}/sprints/${id}`, {
        name: request.name,
        goal: request.goal,
        start_date: request.startDate,
        end_date: request.endDate,
        status: request.status,
      }),
    );
    this.sprints.reload();
    return this.mapToSprint(response);
  }

  /**
   * Get sprint by ID
   */
  async getSprint(id: string): Promise<Sprint> {
    const response = await firstValueFrom(
      this.http.get<SprintResponse>(`${this.apiUrl}/sprints/${id}`),
    );
    return this.mapToSprint(response);
  }

  /**
   * Delete a sprint
   */
  async deleteSprint(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/sprints/${id}`));
    this.sprints.reload();
  }

  /**
   * Complete a sprint
   */
  async completeSprint(id: string, moveIncompleteToBacklog: boolean): Promise<void> {
    await firstValueFrom(
      this.http.post(`${this.apiUrl}/sprints/${id}/complete`, {
        move_incomplete_to_backlog: moveIncompleteToBacklog,
      }),
    );
    this.sprints.reload();
  }

  /**
   * Get sprint burndown stats
   */
  async getSprintBurndownStats(sprintId: string): Promise<BurndownStatsResponse> {
    return await firstValueFrom(
      this.http.get<BurndownStatsResponse>(`${this.apiUrl}/sprints/${sprintId}/stats/burndown`),
    );
  }

  /**
   * Get sprint issue stats
   */
  async getSprintIssueStats(sprintId: string): Promise<IssueStatsResponse> {
    return await firstValueFrom(
      this.http.get<IssueStatsResponse>(`${this.apiUrl}/sprints/${sprintId}/stats/issues`),
    );
  }

  /**
   * Add an issue to a sprint
   */
  async addIssueToSprint(sprintId: string, issueId: string, order?: number): Promise<void> {
    await firstValueFrom(
      this.http.put(`${this.apiUrl}/sprints/${sprintId}/issues`, {
        issue_id: issueId,
        order: order,
      }),
    );
    // Reload sprints to get updated issue counts
    this.sprints.reload();
  }

  /**
   * Remove an issue from a sprint
   */
  async removeIssueFromSprint(sprintId: string, issueId: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/sprints/${sprintId}/issues/${issueId}`));
    // Reload sprints to get updated issue counts
    this.sprints.reload();
  }

  /**
   * Reorder issues within a sprint
   */
  async reorderSprintIssues(sprintId: string, issueOrders: Record<string, number>): Promise<void> {
    await firstValueFrom(
      this.http.put(`${this.apiUrl}/sprints/${sprintId}/issues/reorder`, {
        issue_orders: issueOrders,
      }),
    );
  }

  /**
   * Get project velocity report
   */
  async getProjectVelocity(projectId: string): Promise<VelocityReportResponse> {
    return await firstValueFrom(
      this.http.get<VelocityReportResponse>(
        `${this.apiUrl}/projects/${projectId}/reports/velocity`,
      ),
    );
  }

  /**
   * Get project cumulative flow report
   */
  async getProjectCumulativeFlow(
    projectId: string,
    days: number = 7,
  ): Promise<CumulativeFlowReportResponse> {
    return await firstValueFrom(
      this.http.get<CumulativeFlowReportResponse>(
        `${this.apiUrl}/projects/${projectId}/reports/cumulative-flow?days=${days}`,
      ),
    );
  }

  /**
   * Get project summary statistics
   */
  async getProjectSummaryStats(projectId: string): Promise<ProjectSummaryStatsResponse> {
    return await firstValueFrom(
      this.http.get<ProjectSummaryStatsResponse>(
        `${this.apiUrl}/projects/${projectId}/reports/summary`,
      ),
    );
  }
}

export interface BurndownStatsResponse {
  sprint_id: string;
  burndown_data: Array<{
    date: string;
    ideal: number;
    actual: number;
  }>;
}

export interface IssueStatsResponse {
  sprint_id: string;
  total_issues: number;
  completed_issues: number;
  in_progress_issues: number;
  todo_issues: number;
  cancelled_issues: number;
  total_story_points: number;
  completed_story_points: number;
  in_progress_story_points: number;
  todo_story_points: number;
}

export interface VelocityDataPoint {
  sprint_id: string;
  sprint_name: string;
  committed: number;
  completed: number;
}

export interface VelocityReportResponse {
  project_id: string;
  velocity_data: VelocityDataPoint[];
}

export interface CumulativeFlowDataPoint {
  date: string;
  todo: number;
  in_progress: number;
  done: number;
}

export interface CumulativeFlowReportResponse {
  project_id: string;
  flow_data: CumulativeFlowDataPoint[];
}

export interface ProjectSummaryStatsResponse {
  project_id: string;
  avg_velocity: number;
  team_members: number;
  cycle_time_days: number;
  sprint_goal_completion: number;
}
