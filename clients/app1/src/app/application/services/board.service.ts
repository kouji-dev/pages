import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

export type BoardType = 'project' | 'group';
export type BoardSwimlaneType = 'none' | 'epic' | 'assignee';
export type BoardListType = 'label' | 'assignee' | 'milestone';

export interface BoardListColumnResponse {
  id: string;
  board_id: string;
  list_type: BoardListType;
  list_config: Record<string, unknown> | null;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface BoardResponse {
  id: string;
  project_id: string;
  organization_id: string | null;
  board_type: BoardType;
  swimlane_type: BoardSwimlaneType;
  name: string;
  description: string | null;
  scope_config: Record<string, unknown> | null;
  is_default: boolean;
  position: number;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface BoardWithListsResponse extends BoardResponse {
  lists: BoardListColumnResponse[];
}

export interface BoardListResponse {
  boards: BoardResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface BoardListColumnListResponse {
  lists: BoardListColumnResponse[];
  total: number;
}

export interface BoardIssueItemResponse {
  id: string;
  issue_number: number;
  key: string;
  project_id: string;
  project_key: string;
  title: string;
  type: string;
  status: string;
  priority: string;
  assignee_id: string | null;
  story_points: number | null;
  label_ids: string[];
  comment_count: number;
  subtask_count: number;
}

export interface BoardListWithIssuesResponse {
  id: string;
  board_id: string;
  list_type: string;
  list_config: Record<string, unknown> | null;
  position: number;
  issues: BoardIssueItemResponse[];
}

export interface SwimlaneAssigneeSummary {
  id: string;
  name: string;
  avatar_url: string | null;
}

export interface BoardSwimlaneResponse {
  swimlane_id: string | null;
  swimlane_title: string;
  assignee: SwimlaneAssigneeSummary | null;
  lists: BoardListWithIssuesResponse[];
}

export interface BoardIssuesResponse {
  lists: BoardListWithIssuesResponse[];
  swimlane_type: BoardSwimlaneType;
  swimlanes: BoardSwimlaneResponse[];
}

export interface CreateBoardRequest {
  name: string;
  description?: string;
  scope_config?: Record<string, unknown>;
  is_default?: boolean;
  position?: number;
}

export interface UpdateBoardRequest {
  name?: string;
  description?: string;
  scope_config?: Record<string, unknown>;
  position?: number;
}

export interface ReorderBoardsRequest {
  board_ids: string[];
}

export interface CreateBoardListRequest {
  list_type: BoardListType;
  list_config?: Record<string, unknown>;
}

export interface UpdateBoardListRequest {
  position?: number;
  list_config?: Record<string, unknown>;
}

export interface MoveBoardIssueRequest {
  source_list_id: string;
  target_list_id: string;
}

export interface UpdateBoardScopeRequest {
  label_ids?: string[];
  exclude_label_ids?: string[];
  assignee_id?: string;
  milestone_id?: string;
  types?: string[];
  priorities?: string[];
  fixed_user_id?: string;
  reporter_id?: string;
  search_text?: string;
  story_points_min?: number;
  story_points_max?: number;
}

export interface UpdateBoardSwimlanesRequest {
  swimlane_type: BoardSwimlaneType;
}

export interface CreateGroupBoardRequest extends CreateBoardRequest {
  project_ids: string[];
}

export interface SetGroupBoardProjectsRequest {
  project_ids: string[];
}

@Injectable({
  providedIn: 'root',
})
export class BoardService {
  private readonly http = inject(HttpClient);
  private readonly projectsApiUrl = `${environment.apiUrl}/projects`;
  private readonly boardsApiUrl = `${environment.apiUrl}/boards`;
  private readonly boardListsApiUrl = `${environment.apiUrl}/board-lists`;
  private readonly organizationsApiUrl = `${environment.apiUrl}/organizations`;

  async listProjectBoards(
    projectId: string,
    options?: { page?: number; limit?: number; search?: string },
  ): Promise<BoardListResponse> {
    let params = new HttpParams();
    if (options?.page) {
      params = params.set('page', options.page.toString());
    }
    if (options?.limit) {
      params = params.set('limit', options.limit.toString());
    }
    if (options?.search?.trim()) {
      params = params.set('search', options.search.trim());
    }

    return firstValueFrom(
      this.http.get<BoardListResponse>(`${this.projectsApiUrl}/${projectId}/boards`, {
        params,
      }),
    );
  }

  async createProjectBoard(projectId: string, request: CreateBoardRequest): Promise<BoardResponse> {
    return firstValueFrom(
      this.http.post<BoardResponse>(`${this.projectsApiUrl}/${projectId}/boards`, request),
    );
  }

  async reorderProjectBoards(projectId: string, boardIds: string[]): Promise<void> {
    const request: ReorderBoardsRequest = { board_ids: boardIds };
    await firstValueFrom(
      this.http.put(`${this.projectsApiUrl}/${projectId}/boards/reorder`, request),
    );
  }

  async getBoard(boardId: string): Promise<BoardWithListsResponse> {
    return firstValueFrom(this.http.get<BoardWithListsResponse>(`${this.boardsApiUrl}/${boardId}`));
  }

  async updateBoard(boardId: string, request: UpdateBoardRequest): Promise<BoardResponse> {
    return firstValueFrom(this.http.put<BoardResponse>(`${this.boardsApiUrl}/${boardId}`, request));
  }

  async deleteBoard(boardId: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.boardsApiUrl}/${boardId}`));
  }

  async duplicateBoard(boardId: string): Promise<BoardWithListsResponse> {
    return firstValueFrom(
      this.http.post<BoardWithListsResponse>(`${this.boardsApiUrl}/${boardId}/duplicate`, {}),
    );
  }

  async setDefaultBoard(boardId: string): Promise<BoardResponse> {
    return firstValueFrom(
      this.http.put<BoardResponse>(`${this.boardsApiUrl}/${boardId}/set-default`, {}),
    );
  }

  async listBoardLists(boardId: string): Promise<BoardListColumnListResponse> {
    return firstValueFrom(
      this.http.get<BoardListColumnListResponse>(`${this.boardsApiUrl}/${boardId}/lists`),
    );
  }

  async createBoardList(
    boardId: string,
    request: CreateBoardListRequest,
  ): Promise<BoardListColumnResponse> {
    return firstValueFrom(
      this.http.post<BoardListColumnResponse>(`${this.boardsApiUrl}/${boardId}/lists`, request),
    );
  }

  async updateBoardList(
    listId: string,
    request: UpdateBoardListRequest,
  ): Promise<BoardListColumnResponse> {
    return firstValueFrom(
      this.http.put<BoardListColumnResponse>(`${this.boardListsApiUrl}/${listId}`, request),
    );
  }

  async deleteBoardList(listId: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.boardListsApiUrl}/${listId}`));
  }

  async getBoardIssues(boardId: string): Promise<BoardIssuesResponse> {
    return firstValueFrom(
      this.http.get<BoardIssuesResponse>(`${this.boardsApiUrl}/${boardId}/issues`),
    );
  }

  async moveBoardIssue(
    boardId: string,
    issueId: string,
    request: MoveBoardIssueRequest,
  ): Promise<BoardIssueItemResponse> {
    return firstValueFrom(
      this.http.put<BoardIssueItemResponse>(
        `${this.boardsApiUrl}/${boardId}/issues/${issueId}/move`,
        request,
      ),
    );
  }

  async updateBoardScope(
    boardId: string,
    request: UpdateBoardScopeRequest,
  ): Promise<BoardResponse> {
    return firstValueFrom(
      this.http.put<BoardResponse>(`${this.boardsApiUrl}/${boardId}/scope`, request),
    );
  }

  async updateBoardSwimlanes(
    boardId: string,
    request: UpdateBoardSwimlanesRequest,
  ): Promise<BoardResponse> {
    return firstValueFrom(
      this.http.put<BoardResponse>(`${this.boardsApiUrl}/${boardId}/swimlanes`, request),
    );
  }

  async createGroupBoard(
    organizationId: string,
    request: CreateGroupBoardRequest,
  ): Promise<BoardResponse> {
    return firstValueFrom(
      this.http.post<BoardResponse>(
        `${this.organizationsApiUrl}/${organizationId}/boards`,
        request,
      ),
    );
  }

  async setGroupBoardProjects(boardId: string, projectIds: string[]): Promise<void> {
    const request: SetGroupBoardProjectsRequest = { project_ids: projectIds };
    await firstValueFrom(this.http.post(`${this.boardsApiUrl}/${boardId}/projects`, request));
  }
}
