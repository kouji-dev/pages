import { Component, ChangeDetectionStrategy, input, inject, computed } from '@angular/core';
import { Button } from '../../button/button';
import { ListPlugin } from '../plugins/list-plugin';

@Component({
  selector: 'lib-toolbar-list-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="insertList()"
      [attr.title]="type() === 'ul' ? 'Bullet List' : 'Numbered List'"
      [leftIcon]="iconName()"
    />
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
