import { Component, input, ChangeDetectionStrategy, computed } from '@angular/core';

type IssueType = 'task' | 'bug' | 'story' | 'epic';

@Component({
  selector: 'app-issue-type-badge',
  standalone: true,
  template: `
    <span class="issue-type-badge" [class]="'issue-type-badge--' + type()">
      {{ typeLabel() }}
    </span>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-type-badge {
        @apply inline-flex items-center;
        @apply px-2 py-1;
        @apply text-xs font-semibold;
        @apply rounded;
        @apply uppercase;
      }

      .issue-type-badge--task {
        @apply bg-blue-100 text-blue-800;
      }

      .issue-type-badge--bug {
        @apply bg-red-100 text-red-800;
      }

      .issue-type-badge--story {
        @apply bg-green-100 text-green-800;
      }

      .issue-type-badge--epic {
        @apply bg-purple-100 text-purple-800;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssueTypeBadge {
  readonly type = input.required<IssueType>();

  readonly customLabel = input<string | undefined>(undefined);

  readonly typeLabel = computed(() => {
    const customLabel = this.customLabel();
    if (customLabel) return customLabel;

    const labels: Record<IssueType, string> = {
      task: 'Task',
      bug: 'Bug',
      story: 'Story',
      epic: 'Epic',
    };
    return labels[this.type()] || this.type();
  });
}
