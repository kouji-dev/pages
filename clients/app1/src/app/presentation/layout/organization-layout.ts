import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-organization-layout',
  imports: [RouterOutlet],
  template: `
    <div class="organization-layout">
      <router-outlet />
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .organization-layout {
        @apply w-full h-full;
        @apply flex flex-col;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationLayout {}
