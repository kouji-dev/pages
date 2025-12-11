import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { HistoryPlugin } from '../plugins/history-plugin';

@Component({
  selector: 'lib-toolbar-undo-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="undo()"
      [attr.title]="'Undo (Ctrl+Z)'"
      leftIcon="undo"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarUndoButton {
  private readonly plugin = inject(HistoryPlugin);

  undo(): void {
    this.plugin.undo();
  }
}
