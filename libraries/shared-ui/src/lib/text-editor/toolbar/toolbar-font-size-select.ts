import {
  Component,
  ChangeDetectionStrategy,
  inject,
  computed,
  signal,
  effect,
  model,
} from '@angular/core';
import { Select, type SelectOption } from '../../select/select';
import { FontSizePlugin, FontSize } from '../plugins/font-size-plugin';

@Component({
  selector: 'lib-toolbar-font-size-select',
  imports: [Select],
  template: `
    <lib-select
      [options]="sizeOptions()"
      [model]="sizeModel()"
      (modelChange)="onSizeChange($event)"
      [placeholder]="'Size'"
      class="toolbar-font-size-select"
    />
  `,
  styles: [
    `
      @reference "#theme";

      :host {
        display: inline-block;
      }

      .toolbar-font-size-select {
        min-width: 5rem;
      }

      :host ::ng-deep .select-trigger {
        @apply h-8;
        @apply px-2;
        @apply text-sm;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarFontSizeSelect {
  private readonly plugin = inject(FontSizePlugin);

  readonly sizeOptions = signal<SelectOption<FontSize | ''>[]>([
    { value: '', label: 'Default' },
    { value: 'xs', label: 'XS' },
    { value: 'sm', label: 'SM' },
    { value: 'md', label: 'MD' },
    { value: 'lg', label: 'LG' },
    { value: 'xl', label: 'XL' },
  ]);

  readonly sizeModel = signal<FontSize | ''>('');

  constructor() {
    // Sync plugin's current font size to model (when selection changes)
    effect(() => {
      const currentSize = this.plugin.currentFontSize();
      const modelValue = currentSize || '';
      this.sizeModel.set(modelValue);
    });
  }

  onSizeChange(value: FontSize | '' | null): void {
    if (value) {
      this.plugin.setFontSize(value as FontSize);
    } else {
      this.plugin.removeFontSize();
    }
  }
}
