import { Component, input, ChangeDetectionStrategy, computed } from '@angular/core';
import { Icon, IconName } from 'shared-ui';

type IssuePriority = 'low' | 'medium' | 'high' | 'critical';

@Component({
  selector: 'app-issue-priority-indicator',
  standalone: true,
  imports: [Icon],
  template: `
    <span class="issue-priority" [class]="'issue-priority--' + priority()">
      <lib-icon [name]="priorityIcon()" [size]="'xs'" />
      <span>{{ priorityLabel() }}</span>
    </span>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-priority {
        @apply inline-flex items-center gap-1;
        @apply text-xs font-medium;
      }

      .issue-priority--low {
        @apply text-gray-600;
      }

      .issue-priority--medium {
        @apply text-blue-600;
      }

      .issue-priority--high {
        @apply text-orange-600;
      }

      .issue-priority--critical {
        @apply text-red-600;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssuePriorityIndicator {
  readonly priority = input.required<IssuePriority>();

  readonly customLabel = input<string | undefined>(undefined);

  readonly priorityIcon = computed<IconName>(() => {
    const icons: Record<IssuePriority, IconName> = {
      low: 'arrow-down' as IconName,
      medium: 'minus' as IconName,
      high: 'arrow-up' as IconName,
      critical: 'alert-triangle' as IconName,
    };
    return icons[this.priority()] || ('minus' as IconName);
  });

  readonly priorityLabel = computed(() => {
    const customLabel = this.customLabel();
    if (customLabel) return customLabel;

    const labels: Record<IssuePriority, string> = {
      low: 'Low',
      medium: 'Medium',
      high: 'High',
      critical: 'Critical',
    };
    return labels[this.priority()] || this.priority();
  });
}
