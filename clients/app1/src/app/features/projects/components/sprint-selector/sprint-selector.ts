import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  computed,
  inject,
  ViewContainerRef,
} from '@angular/core';
import { Button, Dropdown, Badge, Icon } from 'shared-ui';
import type { IconName } from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { Sprint } from '../../../../application/services/sprint.service';

@Component({
  selector: 'app-sprint-selector',
  standalone: true,
  imports: [Button, Dropdown, Badge, Icon, TranslatePipe],
  template: `
    <lib-button
      variant="outline"
      size="sm"
      [libDropdown]="dropdownTemplate"
      [position]="'below'"
      [containerClass]="'lib-dropdown-panel--fit-content'"
      class="sprint-selector_button"
      #dropdown="libDropdown"
    >
      <div class="sprint-selector_content">
        @if (selectedSprint(); as sprint) {
          <div class="sprint-selector_selected">
            <lib-icon
              [name]="getStatusIcon(sprint.status)"
              [size]="'sm'"
              [class]="getStatusIconClass(sprint.status)"
            />
            <span class="sprint-selector_name">{{ sprint.name }}</span>
            @if (sprint.status === 'active' && daysLeft() !== null) {
              <lib-badge
                variant="default"
                [class]="'sprint-selector_badge sprint-selector_badge--active'"
              >
                {{ daysLeft() }}d
              </lib-badge>
            }
          </div>
        } @else {
          <span class="sprint-selector_placeholder">
            {{ 'sprints.selectSprint' | translate }}
          </span>
        }
        <lib-icon name="chevron-down" [size]="'sm'" class="sprint-selector_chevron" />
      </div>
    </lib-button>

    <ng-template #dropdownTemplate>
      <div class="sprint-selector_dropdown">
        <div class="sprint-selector_dropdown-header">
          <lib-button
            fullWidth
            [variant]="'ghost'"
            [size]="'sm'"
            [leftIcon]="'plus'"
            (clicked)="handleCreateSprint(dropdown)"
            [class]="'sprint-selector_create-button'"
          >
            {{ 'sprints.createNew' | translate }}
          </lib-button>
        </div>

        <div class="sprint-selector_dropdown-separator"></div>

        <div class="sprint-selector_dropdown-list">
          @for (sprint of sortedSprints(); track sprint.id) {
            <div
              class="sprint-selector_dropdown-item"
              [class.sprint-selector_dropdown-item--active]="selectedSprint()?.id === sprint.id"
              (click)="handleSelectSprint(sprint, dropdown)"
            >
              <div class="sprint-selector_dropdown-item-content">
                <lib-icon
                  [name]="getStatusIcon(sprint.status)"
                  [size]="'sm'"
                  [class]="getStatusIconClass(sprint.status)"
                />
                <div class="sprint-selector_dropdown-item-info">
                  <span class="sprint-selector_dropdown-item-name">{{ sprint.name }}</span>
                  <span class="sprint-selector_dropdown-item-dates">
                    {{ formatDate(sprint.startDate) }} - {{ formatDate(sprint.endDate) }}
                  </span>
                </div>
              </div>
              <lib-badge
                variant="default"
                [class]="getStatusBadgeClass(sprint.status, sprint.endDate)"
              >
                {{ getStatusBadgeText(sprint.status, sprint.endDate) }}
              </lib-badge>
            </div>
          }
        </div>
      </div>
    </ng-template>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .sprint-selector_button {
        @apply justify-between;
      }

      .sprint-selector_content {
        @apply flex items-center justify-between;
        @apply gap-2;
        @apply w-full;
      }

      .sprint-selector_selected {
        @apply flex items-center;
        @apply gap-2;
        @apply flex-1;
        @apply min-w-0;
      }

      .sprint-selector_name {
        @apply font-medium;
        @apply text-foreground;
        @apply truncate;
      }

      .sprint-selector_placeholder {
        @apply text-muted-foreground;
        @apply flex-1;
      }

      .sprint-selector_badge {
        @apply text-xs;
        @apply ml-1;
      }

      .sprint-selector_badge--active {
        background-color: hsl(var(--color-primary) / 0.2);
        color: hsl(var(--color-primary));
        border: 0;
      }

      .sprint-selector_chevron {
        @apply text-muted-foreground;
        @apply flex-shrink-0;
      }

      .sprint-selector_dropdown {
        @apply flex flex-col;
      }

      .sprint-selector_dropdown-header {
        @apply p-2;
      }

      .sprint-selector_create-button {
        @apply w-full;
        @apply justify-start;
      }

      .sprint-selector_dropdown-separator {
        @apply border-t;
        @apply border-border;
        @apply my-1;
      }

      .sprint-selector_dropdown-list {
        @apply flex flex-col;
        @apply max-h-[400px];
        @apply overflow-y-auto;
      }

      .sprint-selector_dropdown-item {
        @apply flex items-center justify-between;
        @apply px-3 py-2;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-accent;
      }

      .sprint-selector_dropdown-item--active {
        @apply bg-accent;
      }

      .sprint-selector_dropdown-item-content {
        @apply flex items-center;
        @apply gap-2;
        @apply flex-1;
        @apply min-w-0;
      }

      .sprint-selector_dropdown-item-info {
        @apply flex flex-col;
        @apply gap-0.5;
        @apply min-w-0;
        @apply flex-1;
      }

      .sprint-selector_dropdown-item-name {
        @apply font-medium;
        @apply text-foreground;
        @apply text-sm;
      }

      .sprint-selector_dropdown-item-dates {
        @apply text-xs;
        @apply text-muted-foreground;
      }

      /* Status icon classes */
      .sprint-selector_icon--active {
        color: hsl(var(--color-primary));
      }

      .sprint-selector_icon--completed {
        color: hsl(var(--color-success));
      }

      .sprint-selector_icon--planned {
        color: hsl(var(--color-muted-foreground));
      }

      /* Status badge classes */
      .sprint-selector_status-badge--active {
        background-color: hsl(var(--color-primary) / 0.2);
        color: hsl(var(--color-primary));
        border: 0;
      }

      .sprint-selector_status-badge--completed {
        background-color: hsl(var(--color-success) / 0.2);
        color: hsl(var(--color-success));
        border: 0;
      }

      .sprint-selector_status-badge--planned {
        background-color: hsl(var(--color-muted));
        color: hsl(var(--color-muted-foreground));
        border: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SprintSelector {
  private readonly translateService = inject(TranslateService);

  readonly sprints = input.required<Sprint[]>();
  readonly selectedSprint = input<Sprint | null>(null);
  readonly onSprintSelect = output<Sprint>();
  readonly onCreateSprint = output<void>();

  readonly activeSprints = computed(() => this.sprints().filter((s) => s.status === 'active'));
  readonly plannedSprints = computed(() => this.sprints().filter((s) => s.status === 'planned'));
  readonly completedSprints = computed(() =>
    this.sprints().filter((s) => s.status === 'completed'),
  );

  readonly sortedSprints = computed(() => {
    return [...this.activeSprints(), ...this.plannedSprints(), ...this.completedSprints()];
  });

  readonly daysLeft = computed(() => {
    const sprint = this.selectedSprint();
    if (!sprint || sprint.status !== 'active') return null;
    const today = new Date();
    const endDate = new Date(sprint.endDate);
    const diffTime = endDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  });

  getStatusIcon(status: Sprint['status']): IconName {
    switch (status) {
      case 'active':
        return 'clock';
      case 'completed':
        return 'circle-check';
      case 'planned':
        return 'calendar';
    }
  }

  getStatusIconClass(status: Sprint['status']): string {
    switch (status) {
      case 'active':
        return 'sprint-selector_icon--active';
      case 'completed':
        return 'sprint-selector_icon--completed';
      case 'planned':
        return 'sprint-selector_icon--planned';
    }
  }

  getStatusBadgeClass(status: Sprint['status'], endDate?: Date | string): string {
    if (status === 'active' && endDate) {
      return 'sprint-selector_status-badge--active';
    }
    if (status === 'completed') {
      return 'sprint-selector_status-badge--completed';
    }
    return 'sprint-selector_status-badge--planned';
  }

  getStatusBadgeText(status: Sprint['status'], endDate?: Date | string): string {
    if (status === 'active' && endDate) {
      const today = new Date();
      const end = typeof endDate === 'string' ? new Date(endDate) : endDate;
      const diffTime = end.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return `${diffDays > 0 ? diffDays : 0}d left`;
    }
    if (status === 'completed') {
      return this.translateService.instant('sprints.status.done');
    }
    return this.translateService.instant('sprints.status.planned');
  }

  formatDate(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(d);
  }

  handleSelectSprint(sprint: Sprint, dropdown: Dropdown): void {
    this.onSprintSelect.emit(sprint);
    dropdown.open.set(false);
  }

  handleCreateSprint(dropdown: Dropdown): void {
    this.onCreateSprint.emit();
    dropdown.open.set(false);
  }
}
