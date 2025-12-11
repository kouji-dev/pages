import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { AttachmentPlugin } from '../plugins/attachment-plugin';

@Component({
  selector: 'lib-toolbar-attachment-button',
  imports: [Button],
  template: `
    <input #fileInput type="file" style="display: none;" (change)="handleFileSelect($event)" />
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="fileInput.click()"
      [attr.title]="'Insert Attachment'"
      leftIcon="file"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarAttachmentButton {
  private readonly plugin = inject(AttachmentPlugin);

  handleFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.plugin.insertAttachmentFromFile(file);
      // Reset input so the same file can be selected again
      input.value = '';
    }
  }
}
