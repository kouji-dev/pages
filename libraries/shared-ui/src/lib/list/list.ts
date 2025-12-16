import { Component, input, ChangeDetectionStrategy, TemplateRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ListItem, ListItemData } from './list-item';

@Component({
  selector: 'lib-list',
  imports: [CommonModule, ListItem],
  template: `
    <ul class="list">
      @if (items(); as itemsList) {
        @for (item of itemsList; track item.id || $index) {
          <li class="list_item-wrapper">
            <lib-list-item [item]="item" [itemTemplate]="itemTemplate()" />
            @if (item.children && item.children.length > 0) {
              <div class="list_children">
                <lib-list [items]="item.children" [itemTemplate]="itemTemplate()" />
              </div>
            }
          </li>
        }
      } @else {
        <ng-content />
      }
    </ul>
  `,
  styles: [
    `
      @reference "#theme";

      .list {
        @apply flex flex-col;
        @apply list-none p-0 m-0;
        @apply space-y-0.5;
      }

      .list_item-wrapper {
        @apply list-none;
      }

      .list_children {
        @apply ml-4;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class List {
  items = input<ListItemData[]>();
  itemTemplate = input<TemplateRef<{ $implicit: ListItemData; item: ListItemData }>>();
}
