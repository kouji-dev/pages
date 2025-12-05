import {
  Component,
  input,
  output,
  ChangeDetectionStrategy,
  effect,
  signal,
  OnDestroy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon, IconName } from '../icon/icon';
import { ToastType } from './toast.service';

@Component({
  selector: 'lib-toast',
  imports: [CommonModule, Icon],
  template: `
    <div
      class="toast"
      [class.toast--success]="type() === 'success'"
      [class.toast--error]="type() === 'error'"
      [class.toast--warning]="type() === 'warning'"
      [class.toast--info]="type() === 'info'"
      [class.toast--show]="isVisible()"
    >
      <div class="toast_content">
        <lib-icon [name]="iconName()" size="sm" class="toast_icon" />
        @if (message()) {
          <div class="toast_message">
            <p class="toast_message-text">{{ message() }}</p>
          </div>
        }
        @if (closable()) {
          <button
            class="toast_close"
            (click)="handleClose()"
            aria-label="Close toast"
            type="button"
          >
            <lib-icon name="x" size="xs" />
          </button>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .toast {
        @apply min-w-80 max-w-md;
        @apply rounded-lg shadow-lg;
        @apply p-4;
        @apply mb-3;
        @apply transform transition-all duration-300 ease-out;
        @apply opacity-0 translate-x-full;
        background-color: var(--color-bg-primary);
        border: 1px solid var(--color-border-default);
        margin-bottom: 0.75rem; /* Stack spacing between toasts */
      }

      .toast--show {
        @apply opacity-100 translate-x-0;
      }

      /* Slide in from right */
      .toast {
        animation: slideInRight 0.3s ease-out forwards;
      }

      .toast--show {
        animation: slideInRight 0.3s ease-out forwards;
      }

      .toast_content {
        @apply flex items-start gap-3;
      }

      .toast_icon {
        @apply flex-shrink-0;
        margin-top: 0.125rem;
      }

      .toast_message {
        @apply flex-1 min-w-0;
      }

      .toast_message-text {
        @apply text-sm;
        @apply m-0;
        @apply leading-relaxed;
        color: var(--color-text-primary);
        word-wrap: break-word;
        display: block;
        width: 100%;
      }

      .toast_close {
        @apply flex-shrink-0;
        @apply p-1 rounded-md;
        @apply transition-colors;
        background: transparent;
        border: none;
        color: var(--color-text-tertiary);
        cursor: pointer;
      }

      .toast_close:hover {
        background-color: var(--color-bg-hover);
        color: var(--color-text-primary);
      }

      /* Type variants */
      .toast--success {
        border-left: 4px solid var(--color-success);
      }

      .toast--success .toast_icon {
        color: var(--color-success);
      }

      .toast--error {
        border-left: 4px solid var(--color-error);
      }

      .toast--error .toast_icon {
        color: var(--color-error);
      }

      .toast--warning {
        border-left: 4px solid var(--color-warning);
      }

      .toast--warning .toast_icon {
        color: var(--color-warning);
      }

      .toast--info {
        border-left: 4px solid var(--color-info);
      }

      .toast--info .toast_icon {
        color: var(--color-info);
      }

      /* Animations */
      @keyframes slideInRight {
        from {
          opacity: 0;
          transform: translateX(100%);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }

      @keyframes slideOutRight {
        from {
          opacity: 1;
          transform: translateX(0);
        }
        to {
          opacity: 0;
          transform: translateX(100%);
        }
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Toast implements OnDestroy {
  toastId = '';
  type = input<ToastType>('info');
  message = input<string>(''); // Changed from required to optional with default
  closable = input(true);
  close = output<void>();

  readonly isVisible = signal(false);
  readonly iconName = signal<IconName>('info');

  constructor() {
    // Set icon based on type
    effect(() => {
      const type = this.type();
      const iconMap: Record<ToastType, IconName> = {
        success: 'circle-check',
        error: 'circle-x',
        warning: 'circle-alert',
        info: 'info',
      };
      this.iconName.set(iconMap[type] || 'info');
    });

    // Show toast after a tiny delay for animation
    setTimeout(() => {
      this.isVisible.set(true);
    }, 10);
  }

  ngOnDestroy(): void {
    // Ensure we hide before destroying
    this.isVisible.set(false);
  }

  handleClose(): void {
    this.isVisible.set(false);
    // Delay close emit to allow animation
    setTimeout(() => {
      this.close.emit();
    }, 300);
  }
}
