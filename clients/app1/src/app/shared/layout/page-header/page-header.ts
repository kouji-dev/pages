import {
  Component,
  input,
  ChangeDetectionStrategy,
  TemplateRef,
  signal,
  model,
} from '@angular/core';
import { Button, IconName, Input, Select, SelectOption } from 'shared-ui';
import { CommonModule } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';

export interface PageHeaderAction {
  label: string;
  icon?: IconName;
  variant?: 'primary' | 'secondary' | 'destructive' | 'outline' | 'ghost' | 'link';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick: () => void;
}

export interface PageHeaderFilter {
  type: 'select' | 'input';
  placeholder?: string;
  options?: SelectOption<any>[];
  model: any; // Signal or Model signal
  class?: string;
  leftIcon?: IconName;
}

export interface PageHeaderSearchInput {
  placeholder?: string;
  model: any; // Signal or Model signal
  class?: string;
  leftIcon?: IconName;
}

@Component({
  selector: 'app-page-header',
  imports: [Button, Input, Select, CommonModule, TranslatePipe],
  template: `
    <div class="page-header">
      <div class="page-header_content">
        <div class="page-header_left">
          <h1 class="page-header_title">{{ title() | translate }}</h1>
          @if (subtitle()) {
            <p class="page-header_subtitle">{{ subtitle() | translate }}</p>
          }
        </div>

        <div class="page-header_right">
          <!-- Search Input -->
          @if (searchInput()) {
            <div class="page-header_search-wrapper">
              <lib-input
                [placeholder]="searchInput()!.placeholder || ''"
                [(model)]="searchInput()!.model"
                [leftIcon]="searchInput()!.leftIcon || 'search'"
                [class]="searchInput()!.class || 'page-header_search-input'"
              />
            </div>
          }

          <!-- Filters -->
          @if (filters() && filters()!.length > 0) {
            @for (filter of filters()!; track $index) {
              @if (filter.type === 'select') {
                <lib-select
                  [options]="filter.options || []"
                  [(model)]="filter.model"
                  [class]="filter.class || 'page-header_filter'"
                />
              } @else if (filter.type === 'input') {
                <lib-input
                  [placeholder]="filter.placeholder || ''"
                  [(model)]="filter.model"
                  [leftIcon]="filter.leftIcon || null"
                  [class]="filter.class || 'page-header_filter-input'"
                />
              }
            }
          }

          <!-- Action Button -->
          @if (action(); as actionData) {
            <lib-button
              [variant]="actionData.variant || 'primary'"
              [size]="actionData.size || 'md'"
              [leftIcon]="actionData.icon"
              [disabled]="actionData.disabled"
              (clicked)="actionData.onClick()"
            >
              {{ actionData.label }}
            </lib-button>
          }

          <!-- Action Template -->
          @if (actionTemplate()) {
            <ng-container *ngTemplateOutlet="actionTemplate()!" />
          }
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .page-header {
        @apply w-full;
        @apply py-4;
        @apply px-2 sm:px-4 lg:px-6;
        @apply border-b;
        @apply border-border;
      }

      .page-header_content {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .page-header_left {
        @apply flex flex-col;
      }

      .page-header_title {
        @apply text-3xl font-bold;
        @apply text-foreground;
        margin: 0;
      }

      .page-header_subtitle {
        @apply text-muted-foreground mt-1;
        margin: 0;
      }

      .page-header_right {
        @apply flex items-center gap-3;
      }

      .page-header_search-wrapper {
        @apply relative;
      }

      .page-header_search-input {
        @apply w-64;
      }

      .page-header_filter {
        @apply w-32;
      }

      .page-header_filter-input {
        @apply w-32;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class PageHeader {
  title = input.required<string>();
  subtitle = input<string>();
  action = input<PageHeaderAction>();
  actionTemplate = input<TemplateRef<any>>();
  searchInput = input<PageHeaderSearchInput | null>(null);
  filters = input<PageHeaderFilter[] | null>(null);
}
