import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-strikethrough-button',
  imports: [Button, Icon],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="formatStrikethrough()"
      [attr.title]="'Strikethrough'"
    >
      <lib-icon name="strikethrough" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarStrikethroughButton {
  private readonly plugin = inject(RichTextPlugin);

  formatStrikethrough(): void {
    this.plugin.format('strikethrough');
  }
}
