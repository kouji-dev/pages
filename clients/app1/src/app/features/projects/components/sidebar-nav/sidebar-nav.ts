import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { Button } from 'shared-ui';
import type { IconName } from 'shared-ui';

export interface SidebarNavItem {
  label: string;
  icon: IconName;
  active: boolean;
  onClick: () => void;
}

@Component({
  selector: 'app-sidebar-nav',
  imports: [Button],
  template: `
    <div class="sidebar-nav">
      <ng-content select="[header]" />
      <nav class="sidebar-nav_nav">
        @for (item of items(); track item.label) {
          <lib-button
            variant="ghost"
            size="md"
            [fullWidth]="true"
            [leftIcon]="item.icon"
            [class.sidebar-nav_nav-item--active]="item.active"
            (clicked)="item.onClick()"
            class="sidebar-nav_nav-item"
          >
            {{ item.label }}
          </lib-button>
        }
      </nav>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply h-full;
        @apply flex;
      }

      .sidebar-nav {
        @apply flex flex-col;
        @apply h-full;
        @apply w-full;
        @apply bg-muted;
      }

      :host ::ng-deep [header] {
        @apply p-4;
        @apply border-b;
        @apply border-border;
        @apply bg-background;
      }

      .sidebar-nav_nav {
        @apply flex flex-col;
        @apply gap-2;
        @apply p-4;
        @apply bg-muted;
        @apply flex-1;
        @apply min-h-0;
      }

      .sidebar-nav_nav-item {
        @apply justify-start;
      }

      .sidebar-nav_nav-item--active {
        @apply bg-accent;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SidebarNav {
  readonly items = input.required<SidebarNavItem[]>();
}
