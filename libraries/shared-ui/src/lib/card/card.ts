import { Component, input, output, model, computed } from '@angular/core';

@Component({
  selector: 'lib-card',
  imports: [],
  template: `
    @if (title()) {
      <div class="card" [class.card--large]="size() === 'large'">
        <div class="card_header" [class.card_header--collapsed]="isCollapsed()">
          <h2 class="card_title">{{ title() }}</h2>
          @if (showCloseButton()) {
            <button class="card_close" (click)="onClose.emit()" type="button">
              <span class="card_close-icon">×</span>
            </button>
          }
        </div>
        @if (!isCollapsed()) {
          <div class="card_body">
            <ng-content></ng-content>
          </div>
        }
      </div>
    } @else {
      <div class="card--empty">No content</div>
    }
  `,
  styles: [
    `
      @reference "#theme";

      .card {
        @apply rounded-lg shadow-md bg-white p-6;
      }

      .card_header {
        @apply flex items-center justify-between mb-4;
      }

      .card_title {
        @apply text-xl font-semibold text-gray-900;
      }

      .card_close {
        @apply text-gray-400 hover:text-gray-600 transition-colors cursor-pointer;
        @apply border-none bg-transparent p-1 rounded;
      }

      .card_close-icon {
        @apply text-2xl leading-none;
      }

      .card_body {
        @apply text-gray-700;
      }

      /* Modifiers */
      .card--large {
        @apply p-8;
      }

      .card_header--collapsed {
        @apply mb-0;
      }

      .card--empty {
        @apply text-gray-500 italic p-4 border border-dashed rounded-md;
      }
    `,
  ],
  standalone: true,
})
export class CardComponent {
  // Required input with modern input() API
  title = input.required<string>();

  // Optional inputs with defaults
  size = input<'small' | 'medium' | 'large'>('medium');
  showCloseButton = input(false);

  // Two-way binding with model()
  isCollapsed = model(false);

  // Output with modern output() API
  onClose = output<void>();

  // Computed property example
  cardClass = computed(() => {
    const base = 'card';
    return this.size() === 'large' ? `${base} card--large` : base;
  });
}
