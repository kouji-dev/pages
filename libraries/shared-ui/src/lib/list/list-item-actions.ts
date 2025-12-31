import { Component, input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Button } from '../button/button';
import { IconName } from '../icon/icon';

export interface ListItemAction {
  icon?: IconName;
  label?: string;
  onClick?: () => void;
  variant?: 'primary' | 'link' | 'ghost' | 'secondary' | 'destructive' | 'outline';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

@Component({
  selector: 'lib-list-item-actions',
  imports: [CommonModule, Button],
  template: `
    <div class="list-item-actions">
      @if (actions() && actions()!.length > 0) {
        @for (action of actions(); track $index) {
          <lib-button
            [variant]="action.variant || 'ghost'"
            [size]="action.size || 'sm'"
            [iconOnly]="!action.label"
            [leftIcon]="action.icon"
            [disabled]="action.disabled"
            (clicked)="action.onClick?.()"
            [attr.aria-label]="action.label || action.icon"
          >
            @if (action.label) {
              {{ action.label }}
            }
          </lib-button>
        }
      } @else {
        <ng-content />
      }
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .list-item-actions {
        @apply flex items-center gap-1;
        @apply flex-shrink-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListItemActions {
  actions = input<ListItemAction[]>();
}
