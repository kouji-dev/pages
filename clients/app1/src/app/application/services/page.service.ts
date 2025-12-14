import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';

export interface Page {
  id: string;
  title: string;
  slug: string;
  content?: string;
  spaceId: string;
  parentId?: string;
  authorId: string;
  authorName?: string;
  editorId?: string;
  editorName?: string;
  commentCount?: number;
  children?: Page[];
  createdAt: string;
  updatedAt: string;
}

export interface PageListItemResponse {
  id: string;
  title: string;
  slug: string;
  space_id: string;
  parent_id?: string;
  author_id: string;
  author_name?: string;
  editor_id?: string;
  editor_name?: string;
  comment_count?: number;
  created_at: string;
  updated_at: string;
}

export interface PageListResponse {
  pages: PageListItemResponse[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface PageResponse {
  id: string;
  title: string;
  slug: string;
  content: string;
  space_id: string;
  parent_id?: string;
  author_id: string;
  author_name?: string;
  editor_id?: string;
  editor_name?: string;
  comment_count?: number;
  children?: PageResponse[];
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root',
})
export class PageService {
  private readonly http = inject(HttpClient);
  private readonly navigationService = inject(NavigationService);
  private readonly apiUrl = `${environment.apiUrl}/pages`;

  // Pages list resource using httpResource - driven by URL spaceId
  readonly pages = httpResource<PageListResponse>(() => {
    const spaceId = this.navigationService.currentSpaceId();
    if (!spaceId) return undefined; // Don't load if no space

    const params = new HttpParams().set('space_id', spaceId);
    return `${this.apiUrl}?${params.toString()}`;
  });

  // Single page resource using httpResource - driven by URL pageId
  readonly page = httpResource<PageResponse>(() => {
    const pageId = this.navigationService.currentPageId();
    if (!pageId) return undefined; // Don't load if no page

    return `${this.apiUrl}/${pageId}`;
  });

  // Public accessors for pages list
  readonly pagesList = computed(() => {
    const value = this.pages.value();
    if (!value) return [];
    return (value.pages || []).map((p) => this.mapToPage(p));
  });

  /**
   * Map backend response (snake_case) to frontend model (camelCase)
   */
  private mapToPage(response: PageListItemResponse | PageResponse): Page {
    const children =
      'children' in response && response.children
        ? response.children.map((c) => this.mapToPage(c))
        : undefined;

    return {
      id: response.id,
      title: response.title,
      slug: response.slug,
      content: 'content' in response ? response.content : undefined,
      spaceId: response.space_id,
      parentId: response.parent_id,
      authorId: response.author_id,
      authorName: response.author_name,
      editorId: response.editor_id,
      editorName: response.editor_name,
      commentCount: response.comment_count,
      children,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

  readonly isLoading = computed(() => this.pages.isLoading());
  readonly error = computed(() => this.pages.error());

  readonly isFetchingPages = computed(() => this.isLoading());
  readonly hasPagesError = computed(() => !!this.error());

  // Single page accessors
  readonly currentPage = computed(() => {
    const value = this.page.value();
    if (!value) return null;
    return this.mapToPage(value);
  });

  readonly isFetchingPage = computed(() => this.page.isLoading());
  readonly hasPageError = computed(() => !!this.page.error());
  readonly pageError = computed(() => this.page.error());

  /**
   * Get pages for a specific space
   */
  getPagesBySpace(spaceId: string): Page[] {
    // For now, return all pages and filter client-side
    // In the future, we can add space-specific filtering
    const allPages = this.pagesList();
    return allPages.filter((page) => page.spaceId === spaceId);
  }

  /**
   * Get root pages (pages without parent) for a space
   */
  getRootPages(spaceId: string): Page[] {
    return this.getPagesBySpace(spaceId).filter((page) => !page.parentId);
  }

  /**
   * Build page tree structure
   */
  buildPageTree(spaceId: string): Page[] {
    const allPages = this.getPagesBySpace(spaceId);
    const pageMap = new Map<string, Page>();

    // First pass: create map of all pages
    allPages.forEach((page) => {
      pageMap.set(page.id, { ...page, children: [] });
    });

    // Second pass: build tree structure
    const rootPages: Page[] = [];
    allPages.forEach((page) => {
      const pageWithChildren = pageMap.get(page.id)!;
      if (page.parentId) {
        const parent = pageMap.get(page.parentId);
        if (parent) {
          if (!parent.children) {
            parent.children = [];
          }
          parent.children.push(pageWithChildren);
        }
      } else {
        rootPages.push(pageWithChildren);
      }
    });

    return rootPages;
  }

  /**
   * Reload pages
   */
  reloadPages(): void {
    this.pages.reload();
  }

  /**
   * Fetch a single page by ID
   */
  fetchPage(pageId: string): void {
    this.page.reload();
  }

  /**
   * Reload current page
   */
  reloadCurrentPage(): void {
    this.page.reload();
  }

  /**
   * Create a new page
   */
  async createPage(request: {
    spaceId: string;
    title: string;
    content?: string;
    parentId?: string;
  }): Promise<Page> {
    const requestBody = {
      space_id: request.spaceId,
      title: request.title,
      content: request.content || null,
      parent_id: request.parentId || null,
    };

    const response = await firstValueFrom(this.http.post<PageResponse>(this.apiUrl, requestBody));
    if (!response) {
      throw new Error('Failed to create page: No response from server');
    }

    // Reload pages list to include the new page
    this.reloadPages();

    // Map response to Page (snake_case to camelCase)
    return this.mapToPage(response);
  }

  /**
   * Update a page
   */
  async updatePage(pageId: string, updates: { title?: string; content?: string }): Promise<Page> {
    const response = await firstValueFrom(
      this.http.put<PageResponse>(`${this.apiUrl}/${pageId}`, updates),
    );
    if (!response) {
      throw new Error('Failed to update page: No response from server');
    }

    // Reload pages list and current page to get updated data
    this.reloadPages();
    const currentPageId = this.navigationService.currentPageId();
    if (currentPageId === pageId) {
      this.page.reload();
    }

    // Map response to Page (snake_case to camelCase)
    return this.mapToPage(response);
  }

  /**
   * Delete a page
   */
  async deletePage(pageId: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/${pageId}`));

    // Reload pages list to remove deleted page
    this.reloadPages();
  }
}
