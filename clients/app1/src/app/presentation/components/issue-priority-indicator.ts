import { Component, input, ChangeDetectionStrategy, computed } from '@angular/core';
import { Icon } from 'shared-ui';
import { getIssuePriorityConfig, type IssuePriority } from '../helpers/issue-helpers';

@Component({
  selector: 'app-issue-priority-indicator',
  standalone: true,
  imports: [Icon],
  template: `
    <span class="issue-priority" [class]="badgeClasses()">
      <lib-icon [name]="priorityConfig().icon" [size]="'xs'" [class]="iconClasses()" />
      <span>{{ priorityLabel() }}</span>
    </span>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-priority {
        @apply inline-flex items-center gap-1.5;
        @apply px-2 py-1;
        @apply text-xs font-semibold;
        @apply rounded;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssuePriorityIndicator {
  readonly priority = input.required<IssuePriority>();

  readonly customLabel = input<string | undefined>(undefined);

  readonly priorityConfig = computed(() => getIssuePriorityConfig(this.priority()));

  readonly badgeClasses = computed(() => {
    const config = this.priorityConfig();
    return `${config.bgColor} ${config.textColor}`;
  });

  readonly iconClasses = computed(() => {
    const config = this.priorityConfig();
    return config.iconColor;
  });

  readonly priorityLabel = computed(() => {
    const customLabel = this.customLabel();
    if (customLabel) return customLabel;
    return this.priorityConfig().label;
  });
}
