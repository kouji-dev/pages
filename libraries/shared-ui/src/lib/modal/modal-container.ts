import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'lib-modal-container',
  imports: [CommonModule],
  template: `
    <div class="modal-container">
      <ng-content></ng-content>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .modal-container {
        @apply flex flex-col;
        @apply bg-white rounded-lg shadow-xl;
        @apply w-full;
        @apply overflow-hidden;
        background-color: var(--color-bg-primary);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-lg);
        animation: modalFadeIn 0.2s ease-out;
        max-height: calc(100vh - 4rem);
      }

      /* Animation */
      @keyframes modalFadeIn {
        from {
          opacity: 0;
          transform: scale(0.95);
        }
        to {
          opacity: 1;
          transform: scale(1);
        }
      }

      /* Dark theme support */
      [data-theme='dark'] .modal-container,
      .dark .modal-container {
        background-color: var(--color-bg-primary);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModalContainer {}
