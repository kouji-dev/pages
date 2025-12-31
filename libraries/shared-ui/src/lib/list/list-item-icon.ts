import { Component, input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon, IconName } from '../icon/icon';

@Component({
  selector: 'lib-list-item-icon',
  imports: [CommonModule, Icon],
  template: `
    @if (name()) {
      <lib-icon [name]="name()!" [size]="size()" [color]="color()" class="list-item-icon" />
    }
  `,
  styles: [
    `
      @reference "#theme";

      .list-item-icon {
        @apply flex-shrink-0;
        @apply flex items-center;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListItemIcon {
  name = input<IconName>();
  size = input<'xs' | 'sm' | 'md' | 'lg'>('sm');
  color = input<string>();
}
