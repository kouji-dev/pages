import { Component, input, ChangeDetectionStrategy, TemplateRef } from '@angular/core';
import { Button, IconName } from 'shared-ui';
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

@Component({
  selector: 'app-page-header',
  imports: [Button, CommonModule, TranslatePipe],
  template: `
    <div class="page-header">
      <div class="page-header_content">
        <div>
          <h1 class="page-header_title">{{ title() | translate }}</h1>
          @if (subtitle()) {
            <p class="page-header_subtitle">{{ subtitle() | translate }}</p>
          }
        </div>
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
        @if (actionTemplate()) {
          <ng-container *ngTemplateOutlet="actionTemplate()!" />
        }
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
        @apply max-w-7xl mx-auto;
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .page-header_title {
        @apply text-3xl font-bold;
        @apply text-foreground;
        margin: 0 0 0.25rem 0;
      }

      .page-header_subtitle {
        @apply text-base;
        @apply text-muted-foreground;
        margin: 0;
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
}
