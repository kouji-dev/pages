import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-code-button',
  imports: [Button, Icon],
  template: `
    <lib-button variant="ghost" size="sm" (clicked)="formatCode()" [attr.title]="'Code'">
      <lib-icon name="code" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarCodeButton {
  private readonly plugin = inject(RichTextPlugin);

  formatCode(): void {
    this.plugin.format('code');
  }
}
