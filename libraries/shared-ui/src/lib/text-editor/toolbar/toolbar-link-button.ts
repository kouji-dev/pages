import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { LinkPlugin } from '../plugins/link-plugin';

@Component({
  selector: 'lib-toolbar-link-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="insertLink()"
      [attr.title]="'Link (Ctrl+K)'"
      leftIcon="link"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarLinkButton {
  private readonly plugin = inject(LinkPlugin);

  insertLink(): void {
    this.plugin.insertLink();
  }
}
