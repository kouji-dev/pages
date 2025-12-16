import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon, IconName } from 'shared-ui';

export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

@Component({
  selector: 'app-priority-indicator',
  standalone: true,
  imports: [CommonModule, Icon],
  template: `
    <div
      class="priority-indicator"
      [class.priority-indicator--low]="priority() === 'low'"
      [class.priority-indicator--medium]="priority() === 'medium'"
      [class.priority-indicator--high]="priority() === 'high'"
      [class.priority-indicator--critical]="priority() === 'critical'"
      [title]="label()"
    >
      <lib-icon [name]="iconName()" size="xs" />
      @if (showLabel()) {
        <span class="priority-label">{{ label() }}</span>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .priority-indicator {
        @apply inline-flex items-center gap-1.5;
        @apply text-sm font-medium;
      }

      .priority-indicator--low {
        @apply text-muted-foreground;
      }

      .priority-indicator--medium {
        @apply text-muted-foreground;
      }

      .priority-indicator--high {
        @apply text-warning;
      }

      .priority-indicator--critical {
        @apply text-destructive;
      }
    `,
  ],
})
export class PriorityIndicator {
  priority = input.required<TaskPriority | string>();
  showLabel = input(true);

  readonly label = computed(() => {
    switch (this.priority()) {
      case 'low':
        return 'Low';
      case 'medium':
        return 'Medium';
      case 'high':
        return 'High';
      case 'critical':
        return 'Critical';
      default:
        return 'Unknown';
    }
  });

  readonly iconName = computed<IconName>(() => {
    switch (this.priority()) {
      case 'low':
        return 'arrow-down';
      case 'medium':
        return 'equal'; // Or generic dot
      case 'high':
        return 'arrow-up';
      case 'critical':
        return 'triangle-alert';
      default:
        return 'circle';
    }
  });
}
