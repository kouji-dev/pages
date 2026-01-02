import { Component, ChangeDetectionStrategy, input, output, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Icon, IconName } from '../icon/icon';

export type TabsVariant = 'default' | 'pills';

export interface TabItem {
  label: string;
  value: string;
  icon?: IconName;
  disabled?: boolean;
  routerLink?: string | any[];
  queryParams?: Record<string, any>;
}

@Component({
  selector: 'lib-tabs',
  standalone: true,
  imports: [CommonModule, Icon, RouterLink],
  template: `
    <div class="tabs" [class.tabs--pills]="variant() === 'pills'">
      <div class="tabs-list" [class.tabs-list--pills]="variant() === 'pills'">
        @for (tab of tabs(); track tab.value) {
          @if (variant() === 'pills') {
            <button
              type="button"
              class="tabs-trigger"
              [class.tabs-trigger--active]="computedActiveTab() === tab.value"
              [class.tabs-trigger--disabled]="tab.disabled"
              [disabled]="tab.disabled"
              (click)="handleTabClick(tab)"
            >
              @if (tab.icon) {
                <lib-icon [name]="tab.icon" [size]="'xs'" />
              }
              <span>{{ tab.label }}</span>
            </button>
          } @else {
            <a
              class="tabs-trigger"
              [class.tabs-trigger--active]="computedActiveTab() === tab.value"
              [class.tabs-trigger--disabled]="tab.disabled"
              [routerLink]="tab.routerLink || []"
              [queryParams]="tab.queryParams"
              [attr.aria-disabled]="tab.disabled ? 'true' : null"
              [tabindex]="tab.disabled ? -1 : 0"
              (click)="handleTabClick(tab, $event)"
            >
              @if (tab.icon) {
                <lib-icon [name]="tab.icon" [size]="'sm'" />
              }
              <span>{{ tab.label }}</span>
            </a>
          }
        }
      </div>

      @if (variant() === 'pills' && showContent()) {
        <div class="tabs-content">
          <ng-content />
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .tabs {
        @apply flex flex-col;
        @apply w-full;
        gap: var(--spacing-4);
      }

      .tabs--pills {
        gap: var(--spacing-4);
      }

      .tabs-list {
        @apply flex items-center;
        @apply gap-1;
        @apply border-b;
        @apply border-border;
        @apply mb-0;
      }

      .tabs-list--pills {
        @apply inline-flex items-center justify-start;
        @apply rounded-lg;
        @apply bg-muted;
        @apply p-1;
        @apply text-muted-foreground;
        @apply border-b-0;
        @apply gap-0;
        @apply w-fit;
      }

      .tabs-trigger {
        @apply flex items-center;
        @apply gap-2;
        @apply px-4 py-2.5;
        @apply text-sm font-medium;
        @apply border-b-2;
        @apply -mb-px;
        @apply transition-colors;
        @apply text-muted-foreground;
        @apply border-b-transparent;
        @apply no-underline;
        @apply cursor-pointer;
        @apply bg-transparent;
      }

      .tabs-list--pills .tabs-trigger {
        @apply inline-flex items-center justify-center;
        @apply whitespace-nowrap;
        @apply rounded-md;
        @apply px-3 py-1.5;
        @apply border-b-0;
        @apply -mb-0;
        gap: var(--spacing-2);
        color: var(--color-muted-foreground);
      }

      .tabs-trigger:hover:not(.tabs-trigger--disabled) {
        @apply text-foreground;
      }

      .tabs-list--pills .tabs-trigger:hover:not(.tabs-trigger--disabled) {
        color: var(--color-foreground);
      }

      .tabs-trigger--active {
        @apply border-b-2 border-b-primary;
        @apply text-foreground;
      }

      .tabs-list--pills .tabs-trigger--active {
        @apply bg-background;
        @apply shadow-sm;
        color: var(--color-foreground);
        @apply border-0;
      }

      .tabs-trigger--disabled {
        @apply pointer-events-none;
        @apply opacity-50;
        @apply cursor-not-allowed;
      }

      .tabs-content {
        @apply w-full;
        @apply mt-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Tabs {
  readonly tabs = input.required<TabItem[]>();
  readonly activeTab = input<string>('');
  readonly variant = input<TabsVariant>('default');
  readonly showContent = input<boolean>(true);

  readonly tabChange = output<string>();

  private readonly internalActiveTab = signal<string>('');

  readonly computedActiveTab = computed(() => {
    const active = this.activeTab();
    if (active) {
      return active;
    }
    const internal = this.internalActiveTab();
    if (internal) {
      return internal;
    }
    // Default to first tab if no active tab is set
    return this.tabs()[0]?.value || '';
  });

  handleTabClick(tab: TabItem, event?: Event): void {
    if (tab.disabled) {
      event?.preventDefault();
      return;
    }

    if (this.variant() === 'pills') {
      // For pills variant, we manage state internally and emit event
      event?.preventDefault();
      this.internalActiveTab.set(tab.value);
      this.tabChange.emit(tab.value);
    } else {
      // For default variant with router links, just emit the event
      // The router will handle navigation, but we can still track internally
      this.tabChange.emit(tab.value);
    }
  }
}
