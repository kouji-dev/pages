import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Icon } from 'shared-ui';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

@Component({
  selector: 'app-breadcrumbs',
  imports: [CommonModule, RouterLink, Icon],
  template: `
    <nav class="breadcrumbs" [attr.aria-label]="ariaLabel()">
      <ol class="breadcrumbs_list">
        @for (item of items(); track $index) {
          <li class="breadcrumbs_item">
            @if ($index < items().length - 1) {
              @if (item.href) {
                <a [routerLink]="item.href" class="breadcrumbs_link">
                  {{ item.label }}
                </a>
              } @else {
                <span class="breadcrumbs_label">{{ item.label }}</span>
              }
              <lib-icon name="chevron-right" size="xs" color="muted-foreground" class="breadcrumbs_separator" />
            } @else {
              <span class="breadcrumbs_page">{{ item.label }}</span>
            }
          </li>
        }
      </ol>
    </nav>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .breadcrumbs {
        @apply flex items-center;
      }

      .breadcrumbs_list {
        @apply flex items-center gap-2;
        @apply list-none m-0 p-0;
      }

      .breadcrumbs_item {
        @apply flex items-center gap-2;
      }

      .breadcrumbs_link {
        @apply text-sm text-muted-foreground;
        @apply hover:text-foreground;
        @apply transition-colors;
        @apply no-underline;
      }

      .breadcrumbs_label {
        @apply text-sm text-muted-foreground;
      }

      .breadcrumbs_page {
        @apply text-sm font-medium text-foreground;
      }

      .breadcrumbs_separator {
        @apply flex-shrink-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class Breadcrumbs {
  items = input.required<BreadcrumbItem[]>();
  ariaLabel = input('Breadcrumb navigation');
}

