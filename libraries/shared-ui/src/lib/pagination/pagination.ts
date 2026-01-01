import { Component, input, output, computed, ChangeDetectionStrategy } from '@angular/core';
import { Button } from '../button/button';

@Component({
  selector: 'lib-pagination',
  imports: [Button],
  template: `
    <div class="pagination">
      <p class="pagination_info">
        {{ getStartIndex() }}-{{ getEndIndex() }} of {{ totalItems() }} {{ itemLabel() }}
      </p>
      <div class="pagination_controls">
        <lib-button
          variant="outline"
          size="sm"
          leftIcon="chevron-left"
          [disabled]="currentPage() === 1"
          (clicked)="onPrevious()"
        />
        @for (page of getPageNumbers(); track page) {
          <lib-button
            [variant]="currentPage() === page ? 'primary' : 'outline'"
            size="sm"
            (clicked)="onPageChange(page)"
            class="pagination_button"
          >
            {{ page }}
          </lib-button>
        }
        <lib-button
          variant="outline"
          size="sm"
          leftIcon="chevron-right"
          [disabled]="currentPage() === totalPages()"
          (clicked)="onNext()"
        />
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .pagination {
        @apply flex items-center justify-between pt-6 border-t border-border mt-6;
      }

      .pagination_info {
        @apply text-sm text-muted-foreground;
        margin: 0;
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
