import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Badge, BadgeVariant } from 'shared-ui';

export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done' | 'backlog' | 'canceled';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule, Badge],
  template: `
    <lib-badge [variant]="variant()">
      {{ label() }}
    </lib-badge>
  `,
  styles: [
    `
      @reference "#mainstyles";
    `,
  ],
})
export class StatusBadge {
  status = input.required<TaskStatus | string>();

  readonly variant = computed<BadgeVariant>(() => {
    switch (this.status()) {
      case 'todo':
      case 'backlog':
      case 'canceled':
        return 'default';
      case 'in_progress':
        return 'info'; // Blue
      case 'review':
        return 'warning'; // Orange/Purple mapping depending on exact need, usually warning or info
      case 'done':
        return 'success'; // Green
      default:
        return 'default';
    }
  });

  readonly label = computed(() => {
    switch (this.status()) {
      case 'todo':
        return 'To Do';
      case 'in_progress':
        return 'In Progress';
      case 'review':
        return 'In Review';
      case 'done':
        return 'Done';
      case 'backlog':
        return 'Backlog';
      case 'canceled':
        return 'Canceled';
      default:
        return this.status();
    }
  });
}
