import { Component, ChangeDetectionStrategy, computed, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Badge, Button, Dropdown, EmptyState, Icon } from 'shared-ui';

export interface LabelSelectorItem {
  id: string;
  name: string;
  color: string;
}

@Component({
  selector: 'app-label-selector',
  standalone: true,
  imports: [Button, Badge, Dropdown, Icon, EmptyState, FormsModule],
  template: `
    <lib-button
      variant="outline"
      size="sm"
      [libDropdown]="dropdownTemplate"
      [position]="'below'"
      [containerClass]="'lib-dropdown-panel--fit-content'"
      class="label-selector_button"
    >
      <div class="label-selector_trigger">
        @if (selectedLabels().length > 0) {
          <div class="label-selector_selected">
            @for (label of selectedLabels().slice(0, 2); track label.id) {
              <lib-badge variant="default" size="sm" class="label-selector_chip">
                <span class="label-selector_dot" [style.backgroundColor]="label.color"></span>
                <span class="label-selector_chip-text">{{ label.name }}</span>
              </lib-badge>
            }
            @if (selectedLabels().length > 2) {
              <lib-badge variant="default" size="sm">+{{ selectedLabels().length - 2 }}</lib-badge>
            }
          </div>
        } @else {
          <span class="label-selector_placeholder">{{ placeholder() }}</span>
        }
        <lib-icon name="chevron-down" size="sm" class="label-selector_chevron" />
      </div>
    </lib-button>
    @if (labels().length === 0) {
      <div class="label-selector_alert">
        <lib-empty-state
          title="No labels yet"
          message="Create your first label directly from this form."
          icon="tag"
          actionLabel="Create Label"
          actionIcon="plus"
          (onAction)="handleManageLabelsAction()"
        />
      </div>
    }

    <ng-template #dropdownTemplate>
      <div class="label-selector_panel">
        <div class="label-selector_search">
          <input
            type="search"
            class="label-selector_search-input"
            [value]="searchQuery()"
            (input)="searchQuery.set($any($event.target).value || '')"
            placeholder="Search labels..."
          />
        </div>

        <div class="label-selector_list">
          @if (labels().length === 0) {
            <p class="label-selector_empty">No labels yet. Use "Create Label" to add one.</p>
          } @else if (filteredLabels().length === 0) {
            <p class="label-selector_empty">No labels found.</p>
          } @else {
            @for (label of filteredLabels(); track label.id) {
              <label class="label-selector_item">
                <input
                  type="checkbox"
                  class="label-selector_checkbox"
                  [checked]="isSelected(label.id)"
                  (change)="handleCheckboxChange(label.id, $event)"
                />
                <span class="label-selector_dot" [style.backgroundColor]="label.color"></span>
                <span class="label-selector_name">{{ label.name }}</span>
              </label>
            }
          }
        </div>
      </div>
    </ng-template>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .label-selector_button {
        @apply w-full justify-between;
      }

      .label-selector_trigger {
        @apply flex items-center justify-between gap-2 w-full;
      }

      .label-selector_selected {
        @apply flex items-center gap-1 flex-wrap;
      }

      .label-selector_chip {
        @apply inline-flex items-center gap-1 max-w-[10rem];
      }

      .label-selector_chip-text {
        @apply truncate;
      }

      .label-selector_placeholder {
        @apply text-muted-foreground;
      }

      .label-selector_chevron {
        @apply text-muted-foreground flex-shrink-0;
      }

      .label-selector_panel {
        @apply w-72 p-2 flex flex-col gap-2;
      }

      .label-selector_alert {
        @apply w-full;
        @apply mt-1;
      }

      .label-selector_search-input {
        @apply w-full px-3 py-2 rounded-md border border-border;
        @apply bg-background text-foreground;
        @apply focus:outline-none focus:ring-2 focus:ring-primary;
      }

      .label-selector_list {
        @apply max-h-64 overflow-y-auto flex flex-col;
      }

      .label-selector_item {
        @apply flex items-center gap-2 px-2 py-2 rounded-md cursor-pointer;
        @apply hover:bg-accent;
      }

      .label-selector_checkbox {
        @apply h-4 w-4;
      }

      .label-selector_dot {
        @apply inline-block h-2.5 w-2.5 rounded-full;
      }

      .label-selector_name {
        @apply text-sm text-foreground;
      }

      .label-selector_empty {
        @apply text-sm text-muted-foreground px-2 py-3;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LabelSelector {
  readonly labels = input<LabelSelectorItem[]>([]);
  readonly selectedIds = input<string[]>([]);
  readonly placeholder = input<string>('Select labels');
  readonly selectedIdsChange = output<string[]>();
  readonly manageLabels = output<void>();

  readonly searchQuery = signal('');

  readonly selectedLabels = computed(() => {
    const selectedIdSet = new Set(this.selectedIds());
    return this.labels().filter((label) => selectedIdSet.has(label.id));
  });

  readonly filteredLabels = computed(() => {
    const query = this.searchQuery().trim().toLowerCase();
    if (!query) {
      return this.labels();
    }

    return this.labels().filter((label) => label.name.toLowerCase().includes(query));
  });

  isSelected(labelId: string): boolean {
    return this.selectedIds().includes(labelId);
  }

  handleCheckboxChange(labelId: string, event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    const next = new Set(this.selectedIds());

    if (checked) {
      next.add(labelId);
    } else {
      next.delete(labelId);
    }

    this.selectedIdsChange.emit(Array.from(next));
  }

  handleManageLabelsAction(): void {
    this.manageLabels.emit();
  }
}
