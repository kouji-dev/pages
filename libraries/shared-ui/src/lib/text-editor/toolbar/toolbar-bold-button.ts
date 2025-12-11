import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-bold-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="formatBold()"
      [attr.title]="'Bold (Ctrl+B)'"
      leftIcon="bold"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarBoldButton {
  private readonly plugin = inject(RichTextPlugin);

  formatBold(): void {
    this.plugin.format('bold');
  }
}
