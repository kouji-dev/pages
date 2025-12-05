import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'lib-modal-footer',
  imports: [CommonModule],
  template: `
    <div class="modal-footer">
      <ng-content></ng-content>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .modal-footer {
        @apply flex items-center justify-end gap-3;
        @apply px-6 py-4;
        border-top: 1px solid var(--color-border-divider);
      }

      @media (max-width: 640px) {
        .modal-footer {
          @apply flex-col gap-2;
        }
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModalFooter {}
