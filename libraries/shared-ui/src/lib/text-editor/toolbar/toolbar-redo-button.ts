import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import { HistoryPlugin } from '../plugins/history-plugin';

@Component({
  selector: 'lib-toolbar-redo-button',
  imports: [Button, Icon],
  template: `
    <lib-button variant="ghost" size="sm" (clicked)="redo()" [attr.title]="'Redo (Ctrl+Y)'">
      <lib-icon name="redo" size="sm" />
    </lib-button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarRedoButton {
  private readonly plugin = inject(HistoryPlugin);

  redo(): void {
    this.plugin.redo();
  }
}
