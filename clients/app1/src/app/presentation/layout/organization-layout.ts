import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-organization-layout',
  imports: [RouterOutlet],
  template: ` <router-outlet /> `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply flex flex-col flex-auto;
        @apply w-full;
        @apply min-h-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationLayout {}
