import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-quote-button',
  imports: [Button, Icon],
  template: `
    <lib-button variant="ghost" size="sm" (clicked)="insertQuote()" [attr.title]="'Quote'">
      <lib-icon name="quote" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarQuoteButton {
  private readonly plugin = inject(RichTextPlugin);

  insertQuote(): void {
    this.plugin.insertQuote();
  }
}
