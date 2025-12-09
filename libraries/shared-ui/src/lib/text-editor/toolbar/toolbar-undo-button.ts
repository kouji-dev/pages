import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { HistoryPlugin } from '../plugins/history-plugin';

@Component({
  selector: 'lib-toolbar-undo-button',
  imports: [Button, Icon],
  template: `
    <lib-button variant="ghost" size="sm" (clicked)="undo()" [attr.title]="'Undo (Ctrl+Z)'">
      <lib-icon name="undo" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarUndoButton {
  private readonly plugin = inject(HistoryPlugin);

  undo(): void {
    this.plugin.undo();
  }
}
