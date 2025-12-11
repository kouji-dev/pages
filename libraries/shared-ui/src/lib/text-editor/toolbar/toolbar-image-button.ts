import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Button } from '../../button/button';
import { ImagePlugin } from '../plugins/image-plugin';

@Component({
  selector: 'lib-toolbar-image-button',
  imports: [Button],
  template: `
    <input
      #fileInput
      type="file"
      accept="image/*"
      style="display: none;"
      (change)="handleFileSelect($event)"
    />
    <lib-button
      variant="ghost"
      size="sm"
      (clicked)="fileInput.click()"
      [attr.title]="'Insert Image'"
      leftIcon="image"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarImageButton {
  private readonly plugin = inject(ImagePlugin);

  handleFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.plugin.insertImageFromFile(file);
      // Reset input so the same file can be selected again
      input.value = '';
    }
  }
}
