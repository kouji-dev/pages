import { Component, signal, inject } from '@angular/core';
import { Button, Icon, ToastService } from 'shared-ui';

@Component({
  selector: 'app-demo',
  imports: [Button, Icon],
  template: `
    <div class="demo">
      <h1 class="demo_title">Component Library Demo</h1>
      <p class="demo_subtitle">Showcasing shared-ui components</p>

      <!-- Icon Component Showcase -->
      <section class="demo_section">
        <h2 class="demo_section-title">Icon Component</h2>

        <div class="demo_grid">
          <div class="demo_item">
            <h3 class="demo_item-title">Sizes</h3>
            <div class="demo_item-content">
              <lib-icon name="menu" size="xs"></lib-icon>
              <lib-icon name="menu" size="sm"></lib-icon>
              <lib-icon name="menu" size="md"></lib-icon>
              <lib-icon name="menu" size="lg"></lib-icon>
              <lib-icon name="menu" size="xl"></lib-icon>
              <lib-icon name="menu" size="2xl"></lib-icon>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Common Icons</h3>
            <div class="demo_item-content">
              <lib-icon name="menu"></lib-icon>
              <lib-icon name="user"></lib-icon>
              <lib-icon name="search"></lib-icon>
              <lib-icon name="plus"></lib-icon>
              <lib-icon name="x"></lib-icon>
              <lib-icon name="check"></lib-icon>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Animations</h3>
            <div class="demo_item-content">
              <lib-icon name="loader" animation="spin"></lib-icon>
              <lib-icon name="heart" animation="pulse"></lib-icon>
              <lib-icon name="bell" animation="bounce"></lib-icon>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">With Custom Color</h3>
            <div class="demo_item-content">
              <lib-icon name="star" color="#fbbf24"></lib-icon>
              <lib-icon name="heart" color="#ef4444"></lib-icon>
              <lib-icon name="check" color="#10b981"></lib-icon>
            </div>
          </div>
        </div>
      </section>

      <!-- Button Component Showcase -->
      <section class="demo_section">
        <h2 class="demo_section-title">Button Component</h2>

        <div class="demo_grid">
          <div class="demo_item">
            <h3 class="demo_item-title">Variants</h3>
            <div class="demo_item-content">
              <lib-button variant="primary">Primary</lib-button>
              <lib-button variant="secondary">Secondary</lib-button>
              <lib-button variant="danger">Danger</lib-button>
              <lib-button variant="ghost">Ghost</lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Sizes</h3>
            <div class="demo_item-content">
              <lib-button size="sm">Small</lib-button>
              <lib-button size="md">Medium</lib-button>
              <lib-button size="lg">Large</lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">States</h3>
            <div class="demo_item-content">
              <lib-button [disabled]="true">Disabled</lib-button>
              <lib-button [loading]="loadingButton()" (clicked)="toggleLoading()">
                {{ loadingButton() ? 'Loading...' : 'Loading State' }}
              </lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">With Left Icon</h3>
            <div class="demo_item-content">
              <lib-button variant="primary" leftIcon="plus">Add Item</lib-button>
              <lib-button variant="secondary" leftIcon="pencil">Edit</lib-button>
              <lib-button variant="danger" leftIcon="trash">Delete</lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">With Right Icon</h3>
            <div class="demo_item-content">
              <lib-button variant="primary" rightIcon="arrow-right">Next</lib-button>
              <lib-button variant="secondary" rightIcon="chevron-down">Options</lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">With Both Icons</h3>
            <div class="demo_item-content">
              <lib-button variant="primary" leftIcon="download" rightIcon="arrow-right"
                >Download & Go</lib-button
              >
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Icon Only</h3>
            <div class="demo_item-content">
              <lib-button variant="ghost" [iconOnly]="true" leftIcon="settings"></lib-button>
              <lib-button variant="ghost" [iconOnly]="true" leftIcon="bell"></lib-button>
              <lib-button variant="primary" [iconOnly]="true" leftIcon="plus"></lib-button>
            </div>
          </div>
        </div>
      </section>

      <!-- Toast Component Showcase -->
      <section class="demo_section">
        <h2 class="demo_section-title">Toast/Notification Component</h2>

        <div class="demo_grid">
          <div class="demo_item">
            <h3 class="demo_item-title">Toast Types</h3>
            <div class="demo_item-content">
              <lib-button (clicked)="showToast('success')">Success Toast</lib-button>
              <lib-button (clicked)="showToast('error')">Error Toast</lib-button>
              <lib-button (clicked)="showToast('warning')">Warning Toast</lib-button>
              <lib-button (clicked)="showToast('info')">Info Toast</lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Positions</h3>
            <div class="demo_item-content">
              <lib-button (clicked)="showToastAtPosition('top-right')">Top Right</lib-button>
              <lib-button (clicked)="showToastAtPosition('top-left')">Top Left</lib-button>
              <lib-button (clicked)="showToastAtPosition('bottom-right')">Bottom Right</lib-button>
              <lib-button (clicked)="showToastAtPosition('bottom-left')">Bottom Left</lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Custom Duration</h3>
            <div class="demo_item-content">
              <lib-button (clicked)="showLongToast()">Long Duration (10s)</lib-button>
              <lib-button (clicked)="showPermanentToast()">No Auto-Dismiss</lib-button>
            </div>
          </div>
        </div>
      </section>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .demo {
        @apply max-w-7xl mx-auto;
        padding: 2rem;
      }

      .demo_title {
        @apply text-4xl font-bold mb-2;
        color: var(--color-text-primary);
      }

      .demo_subtitle {
        @apply text-lg mb-8;
        color: var(--color-text-secondary);
      }

      .demo_section {
        @apply mb-12;
      }

      .demo_section-title {
        @apply text-2xl font-semibold mb-6;
        color: var(--color-text-primary);
      }

      .demo_grid {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
      }

      .demo_item {
        @apply flex flex-col;
      }

      .demo_item-title {
        @apply text-lg font-medium mb-3;
        color: var(--color-text-primary);
      }

      .demo_item-content {
        @apply flex flex-wrap gap-3 items-start;
      }
    `,
  ],
  standalone: true,
})
export class Demo {
  readonly toast = inject(ToastService);
  readonly loadingButton = signal(false);

  toggleLoading(): void {
    this.loadingButton.update((loading) => !loading);
    if (this.loadingButton()) {
      setTimeout(() => {
        this.loadingButton.set(false);
      }, 1000);
    }
  }

  showToast(type: 'success' | 'error' | 'warning' | 'info'): void {
    const messages = {
      success: 'Operation completed successfully!',
      error: 'An error occurred. Please try again.',
      warning: 'Warning: This action cannot be undone.',
      info: 'Here is some useful information.',
    };

    switch (type) {
      case 'success':
        this.toast.success(messages.success);
        break;
      case 'error':
        this.toast.error(messages.error);
        break;
      case 'warning':
        this.toast.warning(messages.warning);
        break;
      case 'info':
        this.toast.info(messages.info);
        break;
    }
  }

  showToastAtPosition(position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'): void {
    this.toast.show({
      type: 'info',
      message: `Toast positioned at ${position.replace('-', ' ')}`,
      position,
    });
  }

  showLongToast(): void {
    this.toast.show({
      type: 'info',
      message: 'This toast will stay for 10 seconds',
      duration: 10000,
    });
  }

  showPermanentToast(): void {
    this.toast.show({
      type: 'warning',
      message: 'This toast will not auto-dismiss. Click X to close.',
      duration: 0,
    });
  }
}
