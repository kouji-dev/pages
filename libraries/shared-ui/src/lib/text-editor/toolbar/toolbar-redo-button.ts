import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { HistoryPlugin } from '../plugins/history-plugin';

@Component({
  selector: 'lib-toolbar-redo-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="redo()"
      [attr.title]="'Redo (Ctrl+Y)'"
      leftIcon="redo"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarRedoButton {
  private readonly plugin = inject(HistoryPlugin);

  redo(): void {
    this.plugin.redo();
  }
}
