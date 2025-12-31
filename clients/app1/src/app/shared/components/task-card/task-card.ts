import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StatusBadge, TaskStatus } from '../status-badge';
import { PriorityIndicator, TaskPriority } from '../priority-indicator';
import { AvatarStack, AvatarStackItem } from '../avatar-stack';
import { Icon, IconName } from 'shared-ui';

export interface Task {
  id: string;
  title: string;
  status: TaskStatus | string;
  priority: TaskPriority | string;
  type: 'story' | 'task' | 'bug' | 'subtask';
  assignees: AvatarStackItem[];
  code: string; // e.g. "P-123"
}

@Component({
  selector: 'app-task-card',
  standalone: true,
  imports: [CommonModule, StatusBadge, PriorityIndicator, AvatarStack, Icon],
  template: `
    <div class="task-card">
      <div class="task-card_header">
        <span class="task-code">{{ task().code }}</span>
        <lib-icon [name]="typeIcon()" size="xs" class="task-type-icon" />
      </div>

      <h3 class="task-title">{{ task().title }}</h3>

      <div class="task-card_footer">
        <div class="task-meta">
          <app-priority-indicator [priority]="task().priority" [showLabel]="false" />
          <app-status-badge [status]="task().status" />
        </div>

        <div class="task-assignees">
          <app-avatar-stack [items]="task().assignees" [limit]="3" size="xs" />
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .task-card {
        .task-card {
          @apply p-3 rounded-lg bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700 cursor-pointer transition-all relative;
          @apply hover:shadow-md hover:border-primary/60;
        }
      }

      .task-card_header {
        @apply flex items-center justify-between mb-1.5;
      }

      .task-code {
        @apply text-xs text-muted-foreground uppercase font-medium tracking-wide;
      }

      .task-type-icon {
        @apply text-muted-foreground;
      }

      .task-title {
        @apply text-sm font-medium text-foreground mb-3 line-clamp-2;
        @apply leading-snug;
      }

      .task-card_footer {
        @apply flex items-center justify-between mt-auto;
      }

      .task-meta {
        @apply flex items-center gap-2;
      }
    `,
  ],
})
export class TaskCard {
  task = input.required<Task>();

  readonly typeIcon = computed<IconName>(() => {
    switch (this.task().type) {
      case 'story':
        return 'bookmark';
      case 'task':
        return 'square-check';
      case 'bug':
        return 'bug';
      case 'subtask':
        return 'corner-down-right';
      default:
        return 'circle'; // Ensure this is a valid icon name
    }
  });
}
