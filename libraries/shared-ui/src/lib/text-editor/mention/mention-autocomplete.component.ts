import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { Button } from '../../button/button';
import { Icon } from '../../icon/icon';
import type { MentionOption } from '../interfaces/mention-list-provider.interface';

@Component({
  selector: 'lib-text-editor-mention-autocomplete',
  imports: [Button, Icon],
  template: `
    @if (options().length > 0) {
      @for (option of options(); track option.id; let i = $index) {
        <button
          type="button"
          class="te-mention-autocomplete_item"
          [class.te-mention-autocomplete_item--selected]="i === selectedIndex()"
          (click)="selectOption.emit(option)"
        >
          @if (option.avatarUrl) {
            <img
              [src]="option.avatarUrl"
              [alt]="option.label"
              class="te-mention-autocomplete_avatar"
            />
          } @else {
            <div class="te-mention-autocomplete_avatar-placeholder">
              {{ getInitials(option.label) }}
            </div>
          }
          <span class="te-mention-autocomplete_label">{{ option.label }}</span>
        </button>
      }
    } @else {
      <div class="te-mention-autocomplete_empty">
        <span class="te-mention-autocomplete_empty-text">No mentions found</span>
      </div>
    }
  `,
  styles: [
    `
      @reference "#theme";

      .te-mention-autocomplete_item {
        @apply w-full;
        @apply flex items-center gap-2;
        @apply px-3 py-2;
        @apply text-left;
        @apply bg-transparent;
        @apply border-none;
        @apply cursor-pointer;
        @apply hover:bg-bg-hover;
        @apply transition-colors;
      }

      .te-mention-autocomplete_item--selected {
        @apply bg-primary-50;
      }

      .te-mention-autocomplete_avatar {
        @apply w-8 h-8;
        @apply rounded-full;
        @apply object-cover;
        @apply flex-shrink-0;
      }

      .te-mention-autocomplete_avatar-placeholder {
        @apply w-8 h-8;
        @apply rounded-full;
        @apply flex items-center justify-center;
        @apply bg-bg-tertiary;
        @apply text-xs font-semibold;
        @apply text-text-primary;
        @apply flex-shrink-0;
      }

      .te-mention-autocomplete_label {
        @apply text-sm;
        @apply text-text-primary;
      }

      .te-mention-autocomplete_empty {
        @apply px-3 py-2;
        @apply text-center;
      }

      .te-mention-autocomplete_empty-text {
        @apply text-sm;
        @apply text-text-secondary;
        @apply italic;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MentionAutocompleteComponent {
  readonly options = input.required<MentionOption[]>();
  readonly selectedIndex = input<number>(-1);
  readonly selectOption = output<MentionOption>();

  getInitials(name: string): string {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }
}
