import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { RichTextPlugin } from '../plugins/rich-text-plugin';

@Component({
  selector: 'lib-toolbar-italic-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="formatItalic()"
      [attr.title]="'Italic (Ctrl+I)'"
      leftIcon="italic"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarItalicButton {
  private readonly plugin = inject(RichTextPlugin);

  formatItalic(): void {
    this.plugin.format('italic');
  }
}
