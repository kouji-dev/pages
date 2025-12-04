import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  template: `
    <div class="app">
      <header class="app_header">
        <h1 class="app_title">{{ title() }}</h1>
      </header>
      <main class="app_main">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .app {
        @apply min-h-screen bg-gray-50;
      }

      .app_header {
        @apply bg-white shadow-sm border-b border-gray-200;
      }

      .app_title {
        @apply text-2xl font-bold text-gray-900 px-6 py-4;
      }

      .app_main {
        @apply container mx-auto px-6 py-8;
      }
    `,
  ],
})
export class App {
  protected readonly title = signal('Pages - Jira and Confluence Alternative');
}
