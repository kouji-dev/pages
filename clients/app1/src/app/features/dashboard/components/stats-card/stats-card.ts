import { Component, input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon, IconName } from 'shared-ui';

@Component({
  selector: 'app-stats-card',
  imports: [CommonModule, Icon],
  template: `
    <div class="stats-card">
      <div class="stats-card_header">
        <span class="stats-card_title">{{ title() }}</span>
        <lib-icon [name]="icon()" size="sm" class="stats-card_icon" />
      </div>
      <div class="stats-card_content">
        <div class="stats-card_value">{{ value() }}</div>
        <p class="stats-card_change">{{ change() }}</p>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .stats-card {
        @apply rounded-lg shadow-sm bg-card text-card-foreground border border-border;
        @apply p-4;
      }

      .stats-card_header {
        @apply flex items-center justify-between pb-2;
      }

      .stats-card_title {
        @apply text-sm font-medium text-muted-foreground;
      }

      .stats-card_icon {
        @apply text-muted-foreground;
      }

      .stats-card_content {
        @apply mt-2;
      }

      .stats-card_value {
        @apply text-2xl font-bold text-foreground;
      }

      .stats-card_change {
        @apply text-xs text-muted-foreground mt-1;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class StatsCard {
  title = input.required<string>();
  value = input.required<string>();
  icon = input.required<IconName>();
  change = input.required<string>();
}
