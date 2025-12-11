import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-strikethrough-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="formatStrikethrough()"
      [attr.title]="'Strikethrough'"
      leftIcon="strikethrough"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarStrikethroughButton {
  private readonly plugin = inject(RichTextPlugin);

  formatStrikethrough(): void {
    this.plugin.format('strikethrough');
  }
}
