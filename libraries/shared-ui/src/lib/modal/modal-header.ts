import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon } from '../icon/icon';
import { Modal } from './modal';

@Component({
  selector: 'lib-modal-header',
  imports: [CommonModule, Icon],
  template: `
    <div class="modal-header">
      <div class="modal-header_content">
        <h2 class="modal-header_title">
          <ng-content></ng-content>
        </h2>
      </div>
      <button class="modal-header_close" (click)="close()" title="Close modal" type="button">
        <lib-icon name="x" size="sm" />
      </button>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .modal-header {
        @apply flex items-center justify-between;
        @apply px-6 py-4;
        border-bottom: 1px solid var(--color-border-divider);
      }

      .modal-header_content {
        @apply flex-1;
      }

      .modal-header_title {
        @apply text-xl font-semibold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .modal-header_close {
        @apply ml-4;
        @apply flex items-center justify-center;
        @apply p-2 rounded-md;
        @apply transition-colors;
        background: transparent;
        border: none;
        color: var(--color-text-tertiary);
        cursor: pointer;
      }

      .modal-header_close:hover {
        background-color: var(--color-bg-hover);
        color: var(--color-text-primary);
      }

      .modal-header_close:focus-visible {
        outline: 2px solid var(--color-border-focus);
        outline-offset: 2px;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModalHeader {
  private modal = inject(Modal);

  close() {
    this.modal.close();
  }
}
