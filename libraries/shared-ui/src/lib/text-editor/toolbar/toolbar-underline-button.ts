import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-underline-button',
  imports: [Button, Icon],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="formatUnderline()"
      [attr.title]="'Underline (Ctrl+U)'"
    >
      <lib-icon name="underline" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarUnderlineButton {
  private readonly plugin = inject(RichTextPlugin);

  formatUnderline(): void {
    this.plugin.format('underline');
  }
}
