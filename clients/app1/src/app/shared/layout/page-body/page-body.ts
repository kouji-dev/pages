import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-page-body',
  imports: [CommonModule],
  template: `
    <ng-content select="app-page-header" />
    <ng-content />
    <ng-content select="app-page-content" />
    <ng-content select="app-page-footer" />
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply flex flex-col flex-auto;
        @apply w-full;
        @apply h-full;
        @apply min-h-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageBody {}
