import { Component, input, ChangeDetectionStrategy, computed } from '@angular/core';

export type ProgressStatus =
  | 'default'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'todo'
  | 'in-progress'
  | 'done';

@Component({
  selector: 'lib-progress',
  standalone: true,
  template: `
    <div
      class="progress"
      [attr.aria-valuenow]="value()"
      [attr.aria-valuemin]="0"
      [attr.aria-valuemax]="100"
      role="progressbar"
    >
      <div
        class="progress_indicator"
        [class]="indicatorClass()"
        [style.width.%]="value() || 0"
      ></div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .progress {
        @apply relative;
        @apply h-1.5;
        @apply w-full;
        @apply overflow-hidden;
        @apply rounded-full;
        @apply bg-gray-100;
      }

      .progress_indicator {
        @apply h-full;
        @apply flex-1;
        @apply transition-all;
        @apply duration-300;
      }

      .progress_indicator--default {
        @apply bg-blue-500;
      }

      .progress_indicator--success,
      .progress_indicator--done {
        @apply bg-green-500;
      }

      .progress_indicator--warning,
      .progress_indicator--in-progress {
        @apply bg-yellow-500;
      }

      .progress_indicator--error {
        @apply bg-red-500;
      }

      .progress_indicator--info {
        @apply bg-blue-500;
      }

      .progress_indicator--todo {
        @apply bg-gray-400;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Progress {
  readonly value = input<number>(0);
  readonly status = input<ProgressStatus>('default');

  readonly indicatorClass = computed(() => {
    return `progress_indicator--${this.status()}`;
  });
}
