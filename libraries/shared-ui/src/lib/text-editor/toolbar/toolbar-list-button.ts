import { Component, ChangeDetectionStrategy, input, inject, computed } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { ListPlugin } from '../plugins/list-plugin';

@Component({
  selector: 'lib-toolbar-list-button',
  imports: [Button, Icon],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="insertList()"
      [attr.title]="type() === 'ul' ? 'Bullet List' : 'Numbered List'"
    >
      <lib-icon [name]="iconName()" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarListButton {
  private readonly plugin = inject(ListPlugin);
  readonly type = input.required<'ul' | 'ol'>();

  readonly iconName = computed(() => {
    return this.type() === 'ul' ? 'list' : 'list-ordered';
  });

  insertList(): void {
    this.plugin.insertList(this.type());
  }
}
