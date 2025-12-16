import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  signal,
  computed,
  TemplateRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon, IconName } from '../icon/icon';

export interface TableColumn<T = any> {
  key: string;
  label: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
}

export type SortDirection = 'asc' | 'desc' | null;

export interface SortEvent {
  column: string;
  direction: SortDirection;
}

@Component({
  selector: 'lib-table',
  imports: [CommonModule, Icon],
  template: `
    <div class="table">
      <div class="table_container">
        <table class="table_wrapper">
          <thead class="table_head">
            <tr class="table_row table_row--header">
              @for (column of columns(); track column.key) {
                <th
                  class="table_header"
                  [class.table_header--center]="column.align === 'center'"
                  [class.table_header--right]="column.align === 'right'"
                  [class.table_header--sortable]="column.sortable"
                  [class.table_header--sorted]="isColumnSorted(column.key)"
                  [style.width]="column.width"
                  (click)="handleSort(column)"
                >
                  <div class="table_header-content">
                    <span>{{ column.label }}</span>
                    @if (column.sortable) {
                      <div class="table_header-sort">
                        @if (isColumnSorted(column.key)) {
                          <lib-icon
                            [name]="getSortIcon(column.key)"
                            size="xs"
                            class="table_header-sort-icon"
                          />
                        } @else {
                          <lib-icon
                            name="arrow-up-down"
                            size="xs"
                            class="table_header-sort-icon table_header-sort-icon--inactive"
                          />
                        }
                      </div>
                    }
                  </div>
                </th>
              }
              @if (hasActions()) {
                <th class="table_header table_header--actions"></th>
              }
            </tr>
          </thead>
          <tbody class="table_body">
            @for (row of data(); track trackByFn()(row); let idx = $index) {
              <tr
                class="table_row table_row--body"
                [class.table_row--hover]="hoverable()"
                [class.table_row--clickable]="clickable()"
                (click)="handleRowClick(row, idx, $event)"
              >
                @for (column of columns(); track column.key) {
                  <td
                    class="table_cell"
                    [class.table_cell--center]="column.align === 'center'"
                    [class.table_cell--right]="column.align === 'right'"
                  >
                    @if (cellTemplate()) {
                      <ng-container
                        *ngTemplateOutlet="
                          cellTemplate()!;
                          context: { $implicit: row, column: column, index: idx }
                        "
                      />
                    } @else {
                      {{ getCellValue(row, column.key) }}
                    }
                  </td>
                }
                @if (hasActions()) {
                  <td class="table_cell table_cell--actions">
                    @if (actionsTemplate()) {
                      <ng-container
                        *ngTemplateOutlet="
                          actionsTemplate()!;
                          context: { $implicit: row, index: idx }
                        "
                      />
                    }
                  </td>
                }
              </tr>
            } @empty {
              <tr class="table_row table_row--empty">
                <td
                  [attr.colspan]="columns().length + (hasActions() ? 1 : 0)"
                  class="table_cell table_cell--empty"
                >
                  @if (emptyTemplate()) {
                    <ng-container *ngTemplateOutlet="emptyTemplate()!" />
                  } @else {
                    <div class="table_empty-message">{{ emptyMessage() }}</div>
                  }
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .table {
        @apply w-full;
        @apply overflow-hidden;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-background;
      }

      .table_container {
        @apply overflow-x-auto;
      }

      .table_wrapper {
        @apply w-full;
        @apply border-collapse;
      }

      .table_head {
        @apply bg-muted/50;
      }

      .table_row {
        @apply border-b;
        @apply border-border;
      }

      .table_row--header {
        @apply border-b;
      }

      .table_row--body {
        @apply transition-colors;
      }

      .table_row--hover:hover {
        @apply bg-muted/50;
      }

      .table_row--clickable {
        @apply cursor-pointer;
      }

      .table_row--empty {
        @apply border-b-0;
      }

      .table_header {
        @apply px-4 py-3;
        @apply text-left;
        @apply text-sm font-medium;
        @apply text-muted-foreground;
        white-space: nowrap;
      }

      .table_header--center {
        @apply text-center;
      }

      .table_header--right {
        @apply text-right;
      }

      .table_header--sortable {
        @apply cursor-pointer;
        @apply select-none;
        @apply hover:bg-muted;
        @apply transition-colors;
      }

      .table_header--sorted {
        @apply bg-muted;
      }

      .table_header-content {
        @apply flex items-center gap-2;
      }

      .table_header-sort {
        @apply flex items-center;
      }

      .table_header-sort-icon {
        @apply flex-shrink-0;
      }

      .table_header-sort-icon--inactive {
        @apply opacity-40;
      }

      .table_header--actions {
        @apply w-1;
        @apply text-right;
      }

      .table_cell {
        @apply px-4 py-3;
        @apply text-sm;
        @apply text-left;
        @apply text-foreground;
      }

      .table_cell--center {
        @apply text-center;
      }

      .table_cell--right {
        @apply text-right;
      }

      .table_cell--actions {
        @apply text-right;
        white-space: nowrap;
      }

      .table_cell--empty {
        @apply text-center;
        @apply py-12;
        @apply text-muted-foreground;
      }

      .table_empty-message {
        @apply text-sm;
        @apply text-muted-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Table<T = any> {
  readonly data = input.required<T[]>();
  readonly columns = input.required<TableColumn<T>[]>();
  readonly trackByFn = input<(row: T) => any>((row: any) => row.id ?? row);
  readonly hoverable = input(true);
  readonly emptyMessage = input('No data available');
  readonly hasActions = input(false);
  readonly clickable = input(false);
  readonly cellTemplate =
    input<TemplateRef<{ $implicit: T; column: TableColumn<T>; index: number }>>();
  readonly actionsTemplate = input<TemplateRef<{ $implicit: T; index: number }>>();
  readonly emptyTemplate = input<TemplateRef<void>>();

  // Row click output
  readonly rowClick = output<{ row: T; index: number }>();

  // Sorting state
  private readonly sortColumn = signal<string | null>(null);
  private readonly sortDirection = signal<SortDirection>(null);

  // Output event for sorting
  readonly sort = output<SortEvent>();

  readonly currentSort = computed(() => {
    const column = this.sortColumn();
    const direction = this.sortDirection();
    return column && direction ? { column, direction } : null;
  });

  isColumnSorted(columnKey: string): boolean {
    return this.sortColumn() === columnKey && this.sortDirection() !== null;
  }

  getSortIcon(columnKey: string): IconName {
    const direction = this.sortDirection();
    if (this.sortColumn() === columnKey && direction) {
      return direction === 'asc' ? ('arrow-up' as IconName) : ('arrow-down' as IconName);
    }
    return 'arrow-up-down' as IconName;
  }

  handleSort(column: TableColumn<T>): void {
    if (!column.sortable) {
      return;
    }

    const currentColumn = this.sortColumn();
    const currentDirection = this.sortDirection();

    if (currentColumn === column.key) {
      // Cycle through: asc -> desc -> null
      if (currentDirection === 'asc') {
        this.sortDirection.set('desc');
      } else if (currentDirection === 'desc') {
        this.sortDirection.set(null);
        this.sortColumn.set(null);
      }
    } else {
      // New column, start with asc
      this.sortColumn.set(column.key);
      this.sortDirection.set('asc');
    }

    const direction = this.sortDirection();
    if (direction) {
      this.sort.emit({ column: column.key, direction });
    } else {
      this.sort.emit({ column: '', direction: null });
    }
  }

  handleRowClick(row: T, index: number, event?: Event): void {
    if (!this.clickable()) {
      return;
    }
    // Don't trigger row click if clicking on a sortable header or button
    if (event) {
      const target = event.target as HTMLElement;
      if (
        target.closest('.table_header--sortable') ||
        target.closest('button') ||
        target.closest('a')
      ) {
        return;
      }
    }
    this.rowClick.emit({ row, index });
  }

  getCellValue(row: T, key: string): string {
    const value = (row as any)[key];
    return value != null ? String(value) : '';
  }
}
