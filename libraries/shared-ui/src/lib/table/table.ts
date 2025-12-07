import { Component, ChangeDetectionStrategy, input, TemplateRef } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface TableColumn<T = any> {
  key: string;
  label: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
}

@Component({
  selector: 'lib-table',
  imports: [CommonModule],
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
                  [style.width]="column.width"
                >
                  {{ column.label }}
                </th>
              }
              @if (hasActions()) {
                <th class="table_header table_header--actions"></th>
              }
            </tr>
          </thead>
          <tbody class="table_body">
            @for (row of data(); track trackByFn()(row); let idx = $index) {
              <tr class="table_row table_row--body" [class.table_row--hover]="hoverable()">
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
        @apply border-border-default;
        @apply bg-bg-primary;
      }

      .table_container {
        @apply overflow-x-auto;
      }

      .table_wrapper {
        @apply w-full;
        @apply border-collapse;
      }

      .table_head {
        @apply bg-bg-tertiary;
      }

      .table_row {
        @apply border-b;
        @apply border-border-default;
      }

      .table_row--header {
        @apply border-b-2;
      }

      .table_row--body {
        @apply transition-colors;
      }

      .table_row--hover:hover {
        @apply bg-bg-secondary;
      }

      .table_row--empty {
        @apply border-b-0;
      }

      .table_header {
        @apply px-4 py-3;
        @apply text-left;
        @apply text-sm font-semibold;
        @apply text-text-primary;
        white-space: nowrap;
      }

      .table_header--center {
        @apply text-center;
      }

      .table_header--right {
        @apply text-right;
      }

      .table_header--actions {
        @apply w-1;
        @apply text-right;
      }

      .table_cell {
        @apply px-4 py-3;
        @apply text-sm;
        @apply text-left;
        @apply text-text-primary;
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
        @apply text-text-secondary;
      }

      .table_empty-message {
        @apply text-sm;
        @apply text-text-secondary;
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
  readonly cellTemplate =
    input<TemplateRef<{ $implicit: T; column: TableColumn<T>; index: number }>>();
  readonly actionsTemplate = input<TemplateRef<{ $implicit: T; index: number }>>();
  readonly emptyTemplate = input<TemplateRef<void>>();

  getCellValue(row: T, key: string): string {
    const value = (row as any)[key];
    return value != null ? String(value) : '';
  }
}
