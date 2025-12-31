import { Component, input, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';

@Component({
  selector: 'app-issue-status-badge',
  standalone: true,
  template: `
    <span class="issue-status-badge" [class]="'issue-status-badge--' + status()">
      {{ statusLabel() }}
    </span>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-status-badge {
        @apply inline-flex items-center;
        @apply px-2 py-1;
        @apply text-xs font-semibold;
        @apply rounded;
        @apply uppercase;
      }

      .issue-status-badge--todo {
        @apply bg-gray-100 text-gray-800;
      }

      .issue-status-badge--in_progress {
        @apply bg-blue-100 text-blue-800;
      }

      .issue-status-badge--done {
        @apply bg-green-100 text-green-800;
      }

      .issue-status-badge--cancelled {
        @apply bg-red-100 text-red-800;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssueStatusBadge {
  private readonly translateService = inject(TranslateService);

  readonly status = input.required<IssueStatus>();

  readonly customLabel = input<string | undefined>(undefined);

  readonly statusLabel = computed(() => {
    const customLabel = this.customLabel();
    if (customLabel) return customLabel;

    const statusKey = this.status();
    return this.translateService.instant(`issues.status.${statusKey}`);
  });
}
