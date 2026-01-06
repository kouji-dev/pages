import { Component, input, output, computed, ChangeDetectionStrategy } from '@angular/core';
import { Button } from '../button/button';
import { Size } from '../types';

const DEFAULT_PAGINATION_SIZE: Size = 'sm';

@Component({
  selector: 'lib-pagination',
  imports: [Button],
  host: {
    '[class.pagination--xs]': "size() === 'xs'",
    '[class.pagination--sm]': "size() === 'sm'",
    '[class.pagination--md]': "size() === 'md'",
    '[class.pagination--lg]': "size() === 'lg'",
  },
  template: `
    <p class="pagination_info">
      {{ getStartIndex() }}-{{ getEndIndex() }} of {{ totalItems() }} {{ itemLabel() }}
    </p>
    <div class="pagination_controls">
      <lib-button
        variant="outline"
        [size]="size()"
        leftIcon="chevron-left"
        [disabled]="currentPage() === 1"
        (clicked)="onPrevious()"
      />
      @for (page of getPageNumbers(); track page) {
        <lib-button
          [variant]="currentPage() === page ? 'primary' : 'outline'"
          [size]="size()"
          (clicked)="onPageChange(page)"
          class="pagination_button"
        >
          {{ page }}
        </lib-button>
      }
      <lib-button
        variant="outline"
        [size]="size()"
        leftIcon="chevron-right"
        [disabled]="currentPage() === totalPages()"
        (clicked)="onNext()"
      />
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      :host {
        @apply flex items-center justify-between border-t border-border;
      }

      :host.pagination--xs {
        @apply p-2;
      }

      :host.pagination--sm {
        @apply p-3;
      }

      :host.pagination--md {
        @apply p-4;
      }

      :host.pagination--lg {
        @apply p-5;
      }

      .pagination_info {
        @apply text-muted-foreground;
        margin: 0;
      }

      .pagination--xs .pagination_info {
        @apply text-xs;
      }

      .pagination--sm .pagination_info {
        @apply text-sm;
      }

      .pagination--md .pagination_info {
        @apply text-sm;
      }

      .pagination--lg .pagination_info {
        @apply text-base;
      }

      .pagination_controls {
        @apply flex items-center gap-2;
      }

      .pagination_button {
        @apply min-w-[2.5rem];
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class Pagination {
  currentPage = input.required<number>();
  totalItems = input.required<number>();
  itemsPerPage = input.required<number>();
  itemLabel = input<string>('items');
  size = input<Size>(DEFAULT_PAGINATION_SIZE);
  pageChange = output<number>();

  readonly totalPages = computed(() => {
    return Math.ceil(this.totalItems() / this.itemsPerPage());
  });

  getStartIndex(): number {
    return (this.currentPage() - 1) * this.itemsPerPage() + 1;
  }

  getEndIndex(): number {
    return Math.min(this.currentPage() * this.itemsPerPage(), this.totalItems());
  }

  getPageNumbers(): number[] {
    return Array.from({ length: this.totalPages() }, (_, i) => i + 1);
  }

  onPrevious(): void {
    if (this.currentPage() > 1) {
      this.pageChange.emit(this.currentPage() - 1);
    }
  }

  onNext(): void {
    if (this.currentPage() < this.totalPages()) {
      this.pageChange.emit(this.currentPage() + 1);
    }
  }

  onPageChange(page: number): void {
    this.pageChange.emit(page);
  }
}
