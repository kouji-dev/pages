import { Component, input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Button } from '../button/button';
import { IconName } from '../icon/icon';

export interface ListHeaderAction {
  icon: IconName;
  label?: string;
  onClick?: () => void;
}

@Component({
  selector: 'lib-list-header',
  imports: [CommonModule, Button],
  template: `
    <div class="list-header">
      <div class="list-header_content">
        @if (title()) {
          <div class="list-header_title">{{ title() }}</div>
        }
        @if (actions() && actions()!.length > 0) {
          <div class="list-header_actions">
            @for (action of actions(); track $index) {
              <lib-button
                variant="ghost"
                size="sm"
                [iconOnly]="!action.label"
                [leftIcon]="action.icon"
                (clicked)="action.onClick?.()"
                [attr.aria-label]="action.label || action.icon"
              >
                @if (action.label) {
                  {{ action.label }}
                }
              </lib-button>
            }
          </div>
        }
      </div>
      <div class="list-header_projected">
        <ng-content />
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .list-header {
        @apply flex flex-col;
        @apply gap-2;
      }

      .list-header_content {
        @apply flex items-center justify-between;
        @apply gap-2;
      }

      .list-header_title {
        @apply text-xs font-semibold;
        @apply text-muted-foreground;
        @apply uppercase tracking-wider;
      }

      .list-header_actions {
        @apply flex items-center;
        @apply gap-1;
      }

      .list-header_projected {
        @apply w-full;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListHeader {
  title = input<string>();
  actions = input<ListHeaderAction[]>();
}
