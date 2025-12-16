import { Component, ChangeDetectionStrategy} from '@angular/core';
import { BaseLayout } from './base-layout';

@Component({
  selector: 'app-authenticated-layout',
  imports: [BaseLayout],
  template: `
    <app-base-layout>
      <!-- Footer links slot -->
      <div slot="footer-links">
        <!-- Footer links will be added here -->
      </div>
    </app-base-layout>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AuthenticatedLayout {}
