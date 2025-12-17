import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'lib-list-item-label',
  imports: [CommonModule],
  template: `
    <span class="list-item-label">
      <ng-content />
    </span>
  `,
  styles: [
    `
      @reference "#theme";

      .list-item-label {
        @apply flex-1 truncate;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListItemLabel {}
