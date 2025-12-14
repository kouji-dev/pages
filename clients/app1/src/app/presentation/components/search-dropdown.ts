import {
  Component,
  ChangeDetectionStrategy,
  signal,
  inject,
  effect,
  HostListener,
  ElementRef,
  ViewChild,
  TemplateRef,
  input,
} from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Icon, Button } from 'shared-ui';
import {
  SearchService,
  SearchResultItem,
  EntityType,
} from '../../application/services/search.service';
import { NavigationService } from '../../application/services/navigation.service';
import { debounceTime, Subject } from 'rxjs';

interface GroupedResults {
  type: EntityType;
  label: string;
  icon: string;
  items: SearchResultItem[];
}

@Component({
  selector: 'app-search-dropdown',
  imports: [CommonModule, Icon, Button],
  template: `
    <div class="search-dropdown" #dropdownContainer>
      @if (isLoading()) {
        <div class="search-dropdown_loading">
          <lib-icon name="loader" size="md" class="search-dropdown_loading-icon" />
          <span class="search-dropdown_loading-text">Searching...</span>
        </div>
      } @else if (groupedResults().length === 0 && query().trim().length > 0) {
        <div class="search-dropdown_empty">
          <lib-icon name="search" size="md" />
          <span>No results found</span>
        </div>
      } @else if (groupedResults().length > 0) {
        <div class="search-dropdown_results">
          @for (group of groupedResults(); track group.type) {
            <div class="search-dropdown_group">
              <div class="search-dropdown_group-header">
                <lib-icon [name]="group.icon" size="sm" />
                <span class="search-dropdown_group-title">{{ group.label }}</span>
                <span class="search-dropdown_group-count">({{ group.items.length }})</span>
              </div>
              <div class="search-dropdown_group-items">
                @for (item of group.items; track item.id) {
                  <button
                    type="button"
                    class="search-dropdown_item"
                    (click)="handleItemClick(item)"
                    [attr.aria-label]="'Go to ' + item.title"
                  >
                    <div class="search-dropdown_item-content">
                      <div
                        class="search-dropdown_item-title"
                        [innerHTML]="highlightText(item.title, query())"
                      ></div>
                      @if (item.snippet) {
                        <div
                          class="search-dropdown_item-snippet"
                          [innerHTML]="highlightText(item.snippet, query())"
                        ></div>
                      }
                    </div>
                    <lib-icon name="arrow-right" size="xs" class="search-dropdown_item-arrow" />
                  </button>
                }
              </div>
            </div>
          }
        </div>
      } @else {
        <div class="search-dropdown_empty">
          <lib-icon name="search" size="md" />
          <span>Start typing to search...</span>
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .search-dropdown {
        @apply bg-bg-primary;
        @apply border border-border-default;
        @apply rounded-lg;
        @apply shadow-lg;
        @apply max-h-[600px];
        @apply overflow-y-auto;
        @apply w-full;
        min-width: 500px;
        max-width: 800px;
      }

      .search-dropdown_loading,
      .search-dropdown_empty {
        @apply flex flex-col items-center justify-center;
        @apply p-8;
        @apply gap-3;
        @apply text-text-secondary;
      }

      .search-dropdown_loading-icon {
        @apply animate-spin;
      }

      .search-dropdown_loading-text {
        @apply text-sm;
      }

      .search-dropdown_results {
        @apply flex flex-col;
      }

      .search-dropdown_group {
        @apply flex flex-col;
        @apply border-b border-border-default;
        @apply last:border-b-0;
      }

      .search-dropdown_group-header {
        @apply flex items-center;
        @apply gap-2;
        @apply px-4 py-2;
        @apply bg-bg-secondary;
        @apply text-sm font-semibold;
        @apply text-text-primary;
      }

      .search-dropdown_group-title {
        @apply flex-1;
      }

      .search-dropdown_group-count {
        @apply text-xs;
        @apply text-text-tertiary;
        @apply font-normal;
      }

      .search-dropdown_group-items {
        @apply flex flex-col;
      }

      .search-dropdown_item {
        @apply flex items-center;
        @apply gap-3;
        @apply px-4 py-3;
        @apply w-full;
        @apply text-left;
        @apply bg-transparent;
        @apply border-none;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-bg-hover;
      }

      .search-dropdown_item-content {
        @apply flex-1;
        @apply min-w-0;
      }

      .search-dropdown_item-title {
        @apply text-sm font-medium;
        @apply text-text-primary;
        @apply mb-1;
      }

      .search-dropdown_item-title ::ng-deep mark {
        @apply bg-pages-highlight-bg;
        /* Keep original text color for better contrast */
        @apply font-semibold;
        @apply px-0.5;
        @apply rounded;
      }

      .search-dropdown_item-snippet {
        @apply text-xs;
        @apply text-text-secondary;
        @apply line-clamp-1;
      }

      .search-dropdown_item-snippet ::ng-deep mark {
        @apply bg-pages-highlight-bg;
        /* Keep original text color for better contrast */
        @apply font-semibold;
        @apply px-0.5;
        @apply rounded;
      }

      .search-dropdown_item-arrow {
        @apply flex-shrink-0;
        @apply text-text-tertiary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SearchDropdown {
  private readonly router = inject(Router);
  private readonly searchService = inject(SearchService);
  private readonly navigationService = inject(NavigationService);

  @ViewChild('dropdownContainer', { static: false }) dropdownContainer?: ElementRef<HTMLDivElement>;

  readonly query = input.required<string>();
  readonly isLoading = signal<boolean>(false);
  readonly results = signal<{
    issues: SearchResultItem[];
    pages: SearchResultItem[];
    organizations: SearchResultItem[];
    projects: SearchResultItem[];
    spaces: SearchResultItem[];
  }>({
    issues: [],
    pages: [],
    organizations: [],
    projects: [],
    spaces: [],
  });

  // Debounced search subject
  private readonly searchSubject = new Subject<string>();

  constructor() {
    // Debounce search queries
    this.searchSubject.pipe(debounceTime(300)).subscribe((query) => {
      this.performSearch(query);
    });

    // Watch query changes and trigger debounced search
    effect(() => {
      const q = this.query();
      if (q.trim().length > 0) {
        this.searchSubject.next(q);
      } else {
        this.results.set({
          issues: [],
          pages: [],
          organizations: [],
          projects: [],
          spaces: [],
        });
        this.groupedResults.set([]);
      }
    });

    // Update grouped results when results change
    effect(() => {
      const results = this.results();
      this.updateGroupedResults(results);
    });
  }

  // Group results by entity type
  readonly groupedResults = signal<GroupedResults[]>([]);

  private updateGroupedResults(results: {
    issues: SearchResultItem[];
    pages: SearchResultItem[];
    organizations: SearchResultItem[];
    projects: SearchResultItem[];
    spaces: SearchResultItem[];
  }): void {
    const groups: GroupedResults[] = [];
    const entityConfig: Record<EntityType, { label: string; icon: string }> = {
      issue: { label: 'Issues', icon: 'file-text' },
      page: { label: 'Pages', icon: 'book' },
      organization: { label: 'Organizations', icon: 'building' },
      project: { label: 'Projects', icon: 'folder' },
      space: { label: 'Spaces', icon: 'book-open' },
    };

    if (results.issues.length > 0) {
      groups.push({
        type: 'issue',
        ...entityConfig.issue,
        items: results.issues,
      });
    }
    if (results.pages.length > 0) {
      groups.push({
        type: 'page',
        ...entityConfig.page,
        items: results.pages,
      });
    }
    if (results.organizations.length > 0) {
      groups.push({
        type: 'organization',
        ...entityConfig.organization,
        items: results.organizations,
      });
    }
    if (results.projects.length > 0) {
      groups.push({
        type: 'project',
        ...entityConfig.project,
        items: results.projects,
      });
    }
    if (results.spaces.length > 0) {
      groups.push({
        type: 'space',
        ...entityConfig.space,
        items: results.spaces,
      });
    }

    this.groupedResults.set(groups);
  }

  private async performSearch(query: string): Promise<void> {
    if (!query.trim()) {
      this.groupedResults.set([]);
      return;
    }

    this.isLoading.set(true);
    try {
      const results = await this.searchService.searchGlobal(query, 5);
      this.results.set(results);
      // Grouped results will be updated automatically via effect
    } catch (error) {
      console.error('Search error:', error);
      this.groupedResults.set([]);
    } finally {
      this.isLoading.set(false);
    }
  }

  /**
   * Highlight search terms in text
   */
  highlightText(text: string, query: string): string {
    if (!query || !text) return this.escapeHtml(text);

    const escapedText = this.escapeHtml(text);
    const escapedQuery = this.escapeHtml(query);
    const regex = new RegExp(`(${escapedQuery})`, 'gi');
    return escapedText.replace(regex, '<mark>$1</mark>');
  }

  /**
   * Escape HTML to prevent XSS
   */
  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Handle item click - navigate to detail page
   */
  handleItemClick(item: SearchResultItem): void {
    const organizationId = this.navigationService.currentOrganizationId() || item.organizationId;
    if (!organizationId) return;

    switch (item.entityType) {
      case 'issue':
        if (item.projectId) {
          this.navigationService.navigateToIssue(organizationId, item.projectId, item.id);
        }
        break;
      case 'page':
        if (item.spaceId) {
          this.navigationService.navigateToPage(organizationId, item.spaceId, item.id);
        }
        break;
      case 'organization':
        this.router.navigate(['/app/organizations', item.id]);
        break;
      case 'project':
        this.router.navigate(['/app/organizations', organizationId, 'projects', item.id]);
        break;
      case 'space':
        this.router.navigate(['/app/organizations', organizationId, 'spaces', item.id]);
        break;
    }
  }
}
