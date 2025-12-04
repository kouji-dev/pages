import { Component } from '@angular/core';
import { BaseLayoutComponent } from './layout/base-layout.component';

@Component({
  selector: 'app-root',
  imports: [BaseLayoutComponent],
  template: `
    <app-base-layout>
      <!-- Navigation menu slot -->
      <div slot="nav">
        <!-- Navigation links will be added here -->
      </div>

      <!-- User menu slot -->
      <div slot="user-menu">
        <!-- User menu will be added here -->
      </div>

      <!-- Sidebar navigation slot -->
      <div slot="sidebar-nav">
        <!-- Sidebar navigation links will be added here -->
      </div>

      <!-- Footer links slot -->
      <div slot="footer-links">
        <!-- Footer links will be added here -->
      </div>
    </app-base-layout>
  `,
  styles: [],
})
export class App {}
