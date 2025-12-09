import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-bold-button',
  imports: [Button, Icon],
  template: `
    <lib-button variant="ghost" size="sm" (clicked)="formatBold()" [attr.title]="'Bold (Ctrl+B)'">
      <lib-icon name="bold" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarBoldButton {
  private readonly plugin = inject(RichTextPlugin);

  formatBold(): void {
    this.plugin.format('bold');
  }
}
