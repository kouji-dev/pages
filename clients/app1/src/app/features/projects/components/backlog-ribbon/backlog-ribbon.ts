import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  computed,
  signal,
  inject,
} from '@angular/core';
import { Button, Badge, Icon } from 'shared-ui';
import type { IconName } from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { SprintIssue } from '../../../../application/services/sprint.service';

@Component({
  selector: 'app-backlog-ribbon',
  standalone: true,
  imports: [Badge, Icon, TranslatePipe],
  template: `
    <div class="backlog-ribbon">
      <!-- Header - always visible -->
      <button type="button" (click)="toggleExpanded()" class="backlog-ribbon_header">
        <div class="backlog-ribbon_header-content">
          <lib-icon
            [name]="isExpanded() ? 'chevron-down' : 'chevron-up'"
            [size]="'sm'"
            class="backlog-ribbon_chevron"
          />
          <span class="backlog-ribbon_title">
            {{ 'backlog.title' | translate }}
          </span>
          <lib-badge variant="default" class="backlog-ribbon_badge">
            {{ issues().length }} {{ 'backlog.issues' | translate }}
          </lib-badge>
          <span class="backlog-ribbon_points">
            {{ totalPoints() }} {{ 'backlog.points' | translate }}
          </span>
        </div>
      </button>

      <!-- Expanded content -->
      @if (isExpanded()) {
        <div class="backlog-ribbon_content">
          @if (issues().length === 0) {
            <div class="backlog-ribbon_empty">
              {{ 'backlog.noItems' | translate }}
            </div>
          } @else {
            <div class="backlog-ribbon_list">
              @for (issue of issues(); track issue.id) {
                <div class="backlog-ribbon_item" (click)="handleIssueClick(issue)">
                  <lib-icon
                    [name]="getIssueTypeIcon(issue.type)"
                    [size]="'xs'"
                    [class]="getIssueTypeIconClass(issue.type)"
                  />
                  <span class="backlog-ribbon_item-key">{{ issue.id.substring(0, 8) }}</span>
                  <span class="backlog-ribbon_item-title">{{ issue.title }}</span>
                  <div class="backlog-ribbon_item-footer">
                    @if (issue.priority === 'high') {
                      <lib-icon
                        name="arrow-up"
                        [size]="'xs'"
                        class="backlog-ribbon_priority-icon"
                      />
                    } @else if (issue.priority === 'low') {
                      <lib-icon
                        name="arrow-down"
                        [size]="'xs'"
                        class="backlog-ribbon_priority-icon backlog-ribbon_priority-icon--low"
                      />
                    }
                    @if (issue.storyPoints) {
                      <lib-badge variant="default" class="backlog-ribbon_points-badge">
                        {{ issue.storyPoints }}
                      </lib-badge>
                    }
                  </div>
                </div>
              }
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .backlog-ribbon {
        @apply border-t;
        @apply border-border;
        @apply m-0;
        background-color: hsl(var(--color-card) / 0.5);
      }

      :host {
        @apply m-0;
        @apply block;
      }

      .backlog-ribbon_header {
        @apply w-full;
        @apply flex items-center justify-between;
        @apply px-4 py-2;
        @apply hover:bg-accent/50;
        @apply transition-colors;
        @apply cursor-pointer;
        @apply border-0;
        @apply bg-transparent;
      }

      .backlog-ribbon_header-content {
        @apply flex items-center;
        @apply gap-3;
      }

      .backlog-ribbon_chevron {
        @apply text-muted-foreground;
      }

      .backlog-ribbon_title {
        @apply text-sm font-medium;
        @apply text-foreground;
      }

      .backlog-ribbon_badge {
        @apply text-xs;
      }

      .backlog-ribbon_points {
        @apply text-xs;
        @apply text-muted-foreground;
      }

      .backlog-ribbon_content {
        @apply max-h-48;
        @apply overflow-y-auto;
        @apply border-t;
        @apply border-border/50;
      }

      .backlog-ribbon_empty {
        @apply px-4 py-6;
        @apply text-center;
        @apply text-sm;
        @apply text-muted-foreground;
      }

      .backlog-ribbon_list {
        @apply divide-y;
        @apply divide-border/50;
      }

      .backlog-ribbon_item {
        @apply flex items-center;
        @apply gap-4;
        @apply px-4 py-2;
        @apply hover:bg-accent/50;
        @apply cursor-pointer;
        @apply transition-colors;
      }

      .backlog-ribbon_item-key {
        @apply text-xs font-mono;
        @apply text-muted-foreground;
        @apply w-20;
        @apply shrink-0;
      }

      .backlog-ribbon_item-title {
        @apply text-sm;
        @apply text-foreground;
        @apply flex-1;
        @apply truncate;
      }

      .backlog-ribbon_item-footer {
        @apply flex items-center;
        @apply gap-2;
        @apply shrink-0;
      }

      .backlog-ribbon_priority-icon {
        color: hsl(var(--color-error));
      }

      .backlog-ribbon_priority-icon--low {
        color: hsl(var(--color-muted-foreground));
      }

      .backlog-ribbon_points-badge {
        @apply text-xs;
        @apply h-5;
        @apply min-w-5;
        @apply flex items-center justify-center;
      }

      /* Issue type icon classes */
      .backlog-ribbon_icon--bug {
        color: hsl(var(--color-error));
      }

      .backlog-ribbon_icon--story {
        color: hsl(var(--color-success));
      }

      .backlog-ribbon_icon--task {
        color: hsl(var(--color-warning));
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BacklogRibbon {
  private readonly translateService = inject(TranslateService);

  readonly issues = input.required<SprintIssue[]>();
  readonly onIssueClick = output<SprintIssue>();

  readonly isExpanded = signal(false);

  readonly totalPoints = computed(() => {
    return this.issues().reduce((sum, issue) => sum + (issue.storyPoints || 0), 0);
  });

  toggleExpanded(): void {
    this.isExpanded.update((value) => !value);
  }

  handleIssueClick(issue: SprintIssue): void {
    this.onIssueClick.emit(issue);
  }

  getIssueTypeIcon(type?: SprintIssue['type']): IconName {
    switch (type) {
      case 'bug':
        return 'bug';
      case 'story':
        return 'book-open';
      default:
        return 'folder';
    }
  }

  getIssueTypeIconClass(type?: SprintIssue['type']): string {
    switch (type) {
      case 'bug':
        return 'backlog-ribbon_icon--bug';
      case 'story':
        return 'backlog-ribbon_icon--story';
      default:
        return 'backlog-ribbon_icon--task';
    }
  }
}
