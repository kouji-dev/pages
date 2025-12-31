import { Component, input, ChangeDetectionStrategy } from '@angular/core';

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
      <div class="progress_indicator" [style.width.%]="value() || 0"></div>
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
        background-color: hsl(var(--color-muted));
      }

      .progress_indicator {
        @apply h-full;
        @apply flex-1;
        background-color: hsl(var(--color-primary));
        @apply transition-all;
        @apply duration-300;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Progress {
  readonly value = input<number>(0);
}
