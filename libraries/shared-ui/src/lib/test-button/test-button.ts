import { Component } from '@angular/core';

@Component({
  selector: 'lib-test-button',
  imports: [],
  template: `
    <button class="test-button" type="button">
      <span class="test-button-text">Test Button from Shared UI</span>
    </button>
  `,
  styles: [
    `
      @reference "#theme";

      .test-button {
        @apply bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-2 px-4 rounded-lg transition-colors;
        @apply shadow-md hover:shadow-lg;
      }

      .test-button-text {
        @apply text-base;
      }
    `,
  ],
})
export class TestButton {}
