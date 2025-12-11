import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-underline-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="formatUnderline()"
      [attr.title]="'Underline (Ctrl+U)'"
      leftIcon="underline"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarUnderlineButton {
  private readonly plugin = inject(RichTextPlugin);

  formatUnderline(): void {
    this.plugin.format('underline');
  }
}
