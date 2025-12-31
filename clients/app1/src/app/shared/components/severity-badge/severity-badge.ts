import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Badge, BadgeVariant } from 'shared-ui';

export type Severity = 'low' | 'medium' | 'high' | 'critical';

@Component({
  selector: 'app-severity-badge',
  standalone: true,
  imports: [CommonModule, Badge],
  template: `
    <lib-badge [variant]="badgeVariant()" [size]="'sm'">
      {{ label() }}
    </lib-badge>
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply inline-block;
      }
    `,
  ],
})
export class SeverityBadge {
  severity = input.required<Severity | string>();

  readonly label = computed(() => {
    switch (this.severity()) {
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

  readonly badgeVariant = computed<BadgeVariant>(() => {
    switch (this.severity()) {
      case 'low':
        return 'default';
      case 'medium':
        return 'info';
      case 'high':
        return 'warning';
      case 'critical':
        return 'danger';
      default:
        return 'default';
    }
  });
}
