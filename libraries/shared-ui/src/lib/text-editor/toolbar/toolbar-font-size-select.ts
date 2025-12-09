import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FontSizePlugin, FontSize } from '../plugins/font-size-plugin';

@Component({
  selector: 'lib-toolbar-font-size-select',
  imports: [CommonModule],
  template: `
    <select
      class="toolbar-font-size-select"
      [value]="selectedSize()"
      (change)="onSizeChange($event)"
      [attr.title]="'Font Size'"
    >
      <option value="">Default</option>
      <option value="xs">XS</option>
      <option value="sm">SM</option>
      <option value="md">MD</option>
      <option value="lg">LG</option>
      <option value="xl">XL</option>
    </select>
  `,
  styles: [
    `
      @reference "#theme";

      .toolbar-font-size-select {
        @apply px-2 py-1;
        @apply text-sm;
        @apply border border-border-default;
        @apply rounded;
        @apply bg-bg-primary;
        @apply text-text-primary;
        @apply cursor-pointer;
        @apply focus:outline-none;
        @apply focus:ring-2;
        @apply focus:ring-primary-500;
        @apply focus:border-primary-500;
        @apply transition-colors;
        @apply hover:border-border-hover;
        min-width: 4rem;
        height: 2rem;
      }

      .toolbar-font-size-select:disabled {
        @apply opacity-50;
        @apply cursor-not-allowed;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarFontSizeSelect {
  private readonly plugin = inject(FontSizePlugin);

  readonly selectedSize = computed(() => {
    return this.plugin.currentFontSize() || '';
  });

  onSizeChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    const value = select.value;
    if (value) {
      this.plugin.setFontSize(value as FontSize);
    } else {
      // Remove font size (reset to default)
      this.plugin.removeFontSize();
    }
  }
}
