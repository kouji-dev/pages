import { Component, input, ChangeDetectionStrategy, TemplateRef, ContentChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Icon, IconName } from '../icon/icon';

export interface ListItemData {
  id?: string;
  label: string;
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
  rightIconColor?: string;
  children?: ListItemData[];
  [key: string]: any; // Allow additional properties
}

@Component({
  selector: 'lib-list-item',
  imports: [CommonModule, RouterLink, RouterLinkActive, Icon],
  template: `
    @if (itemTemplate(); as template) {
      <ng-container
        [ngTemplateOutlet]="template"
        [ngTemplateOutletContext]="{ $implicit: item(), item: item() }"
      />
    } @else {
      @if (item().routerLink) {
        <a
          [routerLink]="item().routerLink!"
          [routerLinkActive]="'list-item--active'"
          [routerLinkActiveOptions]="routerLinkActiveOptions()"
          [class.list-item--disabled]="item().disabled"
          class="list-item"
          [class.list-item--active]="item().active"
        >
          @if (item().icon) {
            <lib-icon
              [name]="item().icon!"
              [size]="item().iconSize || 'sm'"
              [color]="item().iconColor"
              class="list-item_icon"
            />
          }
          <span class="list-item_label">{{ item().label }}</span>
          @if (item().rightIcon) {
            <lib-icon
              [name]="item().rightIcon!"
              [size]="item().rightIconSize || 'xs'"
              [color]="item().rightIconColor"
              class="list-item_right-icon"
            />
          }
        </a>
      } @else if (item().href) {
        <a
          [href]="item().href!"
          [class.list-item--disabled]="item().disabled"
          [class.list-item--active]="item().active"
          class="list-item"
        >
          @if (item().icon) {
            <lib-icon
              [name]="item().icon!"
              [size]="item().iconSize || 'sm'"
              [color]="item().iconColor"
              class="list-item_icon"
            />
          }
          <span class="list-item_label">{{ item().label }}</span>
          @if (item().rightIcon) {
            <lib-icon
              [name]="item().rightIcon!"
              [size]="item().rightIconSize || 'xs'"
              [color]="item().rightIconColor"
              class="list-item_right-icon"
            />
          }
        </a>
      } @else {
        <button
          [class.list-item--disabled]="item().disabled"
          [class.list-item--active]="item().active"
          [disabled]="item().disabled"
          class="list-item"
          (click)="handleClick()"
          type="button"
        >
          @if (item().icon) {
            <lib-icon
              [name]="item().icon!"
              [size]="item().iconSize || 'sm'"
              [color]="item().iconColor"
              class="list-item_icon"
            />
          }
          <span class="list-item_label">{{ item().label }}</span>
          @if (item().rightIcon) {
            <lib-icon
              [name]="item().rightIcon!"
              [size]="item().rightIconSize || 'xs'"
              [color]="item().rightIconColor"
              class="list-item_right-icon"
            />
          }
        </button>
      }
    }
  `,
  styles: [
    `
      @reference "#theme";

      .list-item {
        @apply flex items-center gap-3;
        @apply px-2 py-2;
        @apply rounded-md;
        @apply text-sm;
        @apply text-navigation-foreground;
        @apply transition-colors;
        @apply w-full text-left;
        @apply border-none bg-transparent cursor-pointer;
        @apply no-underline;
        @apply hover:bg-navigation-accent hover:text-navigation-accent-foreground;
      }

      .list-item--active {
        @apply bg-navigation-accent text-navigation-accent-foreground font-medium;
      }

      .list-item--disabled {
        @apply opacity-50 cursor-not-allowed;
        @apply pointer-events-none;
      }

      .list-item_icon {
        @apply flex-shrink-0;
      }

      .list-item_label {
        @apply flex-1 truncate;
      }

      .list-item_right-icon {
        @apply flex-shrink-0 ml-auto;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class ListItem {
  item = input.required<ListItemData>();
  itemTemplate = input<TemplateRef<{ $implicit: ListItemData; item: ListItemData }>>();
  routerLinkActiveOptions = input<{ exact: boolean }>({ exact: false });

  handleClick(): void {
    if (!this.item().disabled && this.item().onClick) {
      this.item().onClick!();
    }
  }
}
