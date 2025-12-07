import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'lib-modal-content',
  imports: [CommonModule],
  template: `
    <div class="modal-content">
      <ng-content></ng-content>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .modal-content {
        @apply px-6 py-4;
        @apply flex-1;
        @apply overflow-y-auto;
        @apply min-h-0;
        @apply text-text-primary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModalContent {}
