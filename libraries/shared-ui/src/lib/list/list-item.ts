import {
  Component,
  input,
  ChangeDetectionStrategy,
  TemplateRef,
  ContentChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Icon, IconName } from '../icon/icon';
import { ListItemRow } from './list-item-row';
import { ListItemIcon } from './list-item-icon';
import { ListItemLabel } from './list-item-label';

export type ListItemDataSeparator = {
  type: 'separator';
  [key: string]: any; // Allow additional properties
};

export interface ListItemDataWithChildren {
  id?: string;
  label: string;
  type?: 'item';
  icon?: IconName;
  iconSize?: 'xs' | 'sm' | 'md' | 'lg';
  iconColor?: string;
  href?: string;
  routerLink?: string | any[];
  active?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  rightIcon?: IconName;
  rightIconSize?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive' | 'outline' | 'link';
  children?: ListItemData[];
  itemTemplate?: TemplateRef<any>;
  [key: string]: any; // Allow additional properties
}

export type ListItemData = ListItemDataSeparator | ListItemDataWithChildren;

@Component({
  selector: 'lib-list-item',
  imports: [
    CommonModule,
    RouterLink,
    RouterLinkActive,
    Icon,
    ListItemRow,
    ListItemIcon,
    ListItemLabel,
  ],
  template: `
    @if (item().itemTemplate) {
      <div
        [class.list-item--disabled]="item().disabled"
        [class.list-item--destructive]="item().variant === 'destructive'"
        class="list-item"
        [class.list-item--active]="item().active"
        [attr.data-item-id]="item().id"
      >
        <ng-container
          [ngTemplateOutlet]="item().itemTemplate!"
          [ngTemplateOutletContext]="{ $implicit: item(), item: item() }"
        />
      </div>
    } @else if (itemTemplate(); as template) {
      <div
        [class.list-item--disabled]="item().disabled"
        [class.list-item--destructive]="item().variant === 'destructive'"
        class="list-item"
        [class.list-item--active]="item().active"
        [attr.data-item-id]="item().id"
      >
        <ng-container
          [ngTemplateOutlet]="template"
          [ngTemplateOutletContext]="{ $implicit: item(), item: item() }"
        />
      </div>
    } @else if (item().type === 'separator') {
      <div class="list-item_separator"></div>
    } @else {
      @if (item().type !== 'separator') {
        @let itemData = item();
        @if (itemData.routerLink) {
          <a
            [routerLink]="itemData.routerLink"
            [routerLinkActive]="'list-item--active'"
            [routerLinkActiveOptions]="routerLinkActiveOptions()"
            [class.list-item--disabled]="itemData.disabled"
            [class.list-item--destructive]="itemData.variant === 'destructive'"
            class="list-item"
            [class.list-item--active]="itemData.active"
            [attr.data-item-id]="itemData.id"
          >
            <lib-list-item-row>
              @if (itemData.icon) {
                <lib-list-item-icon
                  [name]="itemData.icon"
                  [size]="itemData.iconSize || 'sm'"
                  [color]="itemData.iconColor"
                />
              }
              <lib-list-item-label>{{ itemData.label }}</lib-list-item-label>
              @if (itemData.rightIcon) {
                <lib-icon
                  [name]="itemData.rightIcon"
                  [size]="itemData.rightIconSize || 'xs'"
                  class="list-item_right-icon"
                />
              }
            </lib-list-item-row>
          </a>
        } @else if (itemData.href) {
          <a
            [href]="itemData.href"
            [class.list-item--disabled]="itemData.disabled"
            [class.list-item--active]="itemData.active"
            [class.list-item--destructive]="itemData.variant === 'destructive'"
            class="list-item"
            [attr.data-item-id]="itemData.id"
          >
            <lib-list-item-row>
              @if (itemData.icon) {
                <lib-list-item-icon
                  [name]="itemData.icon"
                  [size]="itemData.iconSize || 'sm'"
                  [color]="itemData.iconColor"
                />
              }
              <lib-list-item-label>{{ itemData.label }}</lib-list-item-label>
              @if (itemData.rightIcon) {
                <lib-icon
                  [name]="itemData.rightIcon"
                  [size]="itemData.rightIconSize || 'xs'"
                  class="list-item_right-icon"
                />
              }
            </lib-list-item-row>
          </a>
        } @else {
          <button
            [class.list-item--disabled]="itemData.disabled"
            [class.list-item--active]="itemData.active"
            [class.list-item--destructive]="itemData.variant === 'destructive'"
            [disabled]="itemData.disabled"
            class="list-item"
            [attr.data-item-id]="itemData.id"
            (click)="handleClick()"
            type="button"
          >
            <lib-list-item-row>
              @if (itemData.icon) {
                <lib-list-item-icon
                  [name]="itemData.icon"
                  [size]="itemData.iconSize || 'sm'"
                  [color]="itemData.iconColor"
                />
              }
              <lib-list-item-label>{{ itemData.label }}</lib-list-item-label>
              @if (itemData.rightIcon) {
                <lib-icon
                  [name]="itemData.rightIcon"
                  [size]="itemData.rightIconSize || 'xs'"
                  class="list-item_right-icon"
                />
              }
            </lib-list-item-row>
          </button>
        }
      }
    }
  `,
  styles: [
    `
      @reference "#theme";

      .list-item {
        @apply w-full;
        @apply p-0;
      }

      .list-item_icon {
        @apply flex-shrink-0;
        @apply flex items-center;
      }

      .list-item_label {
        @apply flex-1 truncate;
        @apply flex items-center;
      }

      .list-item_right-icon {
        @apply flex-shrink-0 ml-auto;
        @apply flex items-center;
      }

      .list-item_separator {
        @apply h-px;
        @apply bg-border;
        @apply my-1;
        @apply mx-2;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListItem {
  item = input.required<ListItemData>();
  itemTemplate = input<TemplateRef<{ $implicit: ListItemData; item: ListItemData }>>();
  routerLinkActiveOptions = input<{ exact: boolean }>({ exact: false });

  handleClick(): void {
    if (this.item().type === 'separator') {
      return;
    }
    const item = this.item() as ListItemDataWithChildren;
    if (!item.disabled && item.onClick) {
      item.onClick();
    }
  }
}
