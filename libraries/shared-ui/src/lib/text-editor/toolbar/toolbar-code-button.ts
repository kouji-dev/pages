import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-code-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="formatCode()"
      [attr.title]="'Code'"
      leftIcon="code"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarCodeButton {
  private readonly plugin = inject(RichTextPlugin);

  formatCode(): void {
    this.plugin.format('code');
  }
}
