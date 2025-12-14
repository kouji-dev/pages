import { Component, ChangeDetectionStrategy, computed, inject, input } from '@angular/core';
import { PageService, Page } from '../../application/services/page.service';
import { NavigationService } from '../../application/services/navigation.service';

@Component({
  selector: 'app-pages-tree-item',
  imports: [],
  template: `
    <div class="pages-tree-item" [class.pages-tree-item--active]="isActive()">
      <button
        class="pages-tree-item_button"
        [style.padding-left.px]="level() * 16 + 8"
        (click)="handleClick()"
      >
        <span class="pages-tree-item_title">{{ page().title }}</span>
      </button>
      @if (page().children && page()!.children!.length > 0) {
        <div class="pages-tree-item_children">
          @for (child of page()!.children; track child.id) {
            <app-pages-tree-item
              [page]="child"
              [level]="level() + 1"
              [spaceId]="spaceId()"
              [organizationId]="organizationId()"
            />
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .pages-tree-item {
        @apply flex flex-col;
      }

      .pages-tree-item_button {
        @apply w-full;
        @apply px-3 py-2;
        @apply text-left;
        @apply rounded-md;
        @apply text-sm;
        @apply text-text-secondary;
        @apply transition-all;
        @apply hover:bg-bg-tertiary;
        @apply hover:text-text-primary;
        @apply border-none;
        @apply bg-transparent;
        @apply cursor-pointer;
        @apply flex items-center;
        @apply gap-2;
        @apply relative;
      }

      .pages-tree-item--active .pages-tree-item_button {
        @apply bg-bg-tertiary;
        @apply text-text-primary;
        @apply font-medium;
      }

      .pages-tree-item--active .pages-tree-item_button::before {
        content: '';
        @apply absolute left-0 top-0 bottom-0;
        @apply w-1;
        @apply bg-primary-500;
        @apply rounded-r;
      }

      .pages-tree-item_title {
        @apply truncate;
        @apply flex-1;
      }

      .pages-tree-item_children {
        @apply flex flex-col;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PagesTreeItem {
  readonly navigationService = inject(NavigationService);

  readonly page = input.required<Page>();
  readonly level = input.required<number>();
  readonly spaceId = input.required<string>();
  readonly organizationId = input.required<string>();

  readonly isActive = computed(() => {
    const currentPageId = this.navigationService.currentPageId();
    const pageId = this.page().id;
    return currentPageId === pageId;
  });

  handleClick(): void {
    const page = this.page();
    const spaceId = this.spaceId();
    const organizationId = this.organizationId();

    if (page.id && spaceId && organizationId) {
      this.navigationService.navigateToPage(organizationId, spaceId, page.id);
    }
  }
}

@Component({
  selector: 'app-pages-tree',
  imports: [PagesTreeItem],
  template: `
    <div class="pages-tree">
      @if (pageTree().length === 0) {
        <div class="pages-tree_empty">
          <p class="pages-tree_empty-text">No pages yet</p>
        </div>
      } @else {
        <nav class="pages-tree_nav">
          @for (page of pageTree(); track page.id) {
            <app-pages-tree-item
              [page]="page"
              [level]="0"
              [spaceId]="spaceId()"
              [organizationId]="organizationId()"
            />
          }
        </nav>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .pages-tree {
        @apply flex flex-col;
        @apply h-full;
        @apply bg-bg-secondary;
      }

      .pages-tree_empty {
        @apply px-4 py-8;
        @apply text-center;
      }

      .pages-tree_empty-text {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }

      .pages-tree_nav {
        @apply flex-1;
        @apply overflow-auto;
        @apply px-2 py-2;
        @apply bg-bg-secondary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PagesTree {
  readonly pageService = inject(PageService);
  readonly navigationService = inject(NavigationService);

  readonly spaceId = input.required<string>();

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  readonly pageTree = computed(() => {
    const id = this.spaceId();
    if (!id) return [];
    return this.pageService.buildPageTree(id);
  });
}
