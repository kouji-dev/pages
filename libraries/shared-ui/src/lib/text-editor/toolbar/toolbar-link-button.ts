import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { LinkPlugin } from '../plugins/link-plugin';

@Component({
  selector: 'lib-toolbar-link-button',
  imports: [Button, Icon],
  template: `
    <lib-button variant="ghost" size="sm" (clicked)="insertLink()" [attr.title]="'Link (Ctrl+K)'">
      <lib-icon name="link" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarLinkButton {
  private readonly plugin = inject(LinkPlugin);

  insertLink(): void {
    this.plugin.insertLink();
  }
}
