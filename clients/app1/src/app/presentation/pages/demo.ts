import { Component, signal, inject, ViewChild, TemplateRef, ViewContainerRef } from '@angular/core';
import { Button, Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';

@Component({
  selector: 'app-demo',
  imports: [Button, ModalContainer, ModalHeader, ModalContent, ModalFooter],
  template: `
    <div class="demo">
      <h1 class="demo_title">Component Library Demo</h1>
      <p class="demo_subtitle">Showcasing shared-ui components</p>

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
        </div>
      </section>

      <!-- Modal Component Showcase -->
      <section class="demo_section">
        <h2 class="demo_section-title">Modal Component</h2>

        <div class="demo_grid">
          <div class="demo_item">
            <h3 class="demo_item-title">Basic Modal</h3>
            <div class="demo_item-content">
              <lib-button (clicked)="openBasicModal()">Open Basic Modal</lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Size Variants</h3>
            <div class="demo_item-content">
              <lib-button (clicked)="openModal('sm')">Small</lib-button>
              <lib-button (clicked)="openModal('md')">Medium</lib-button>
              <lib-button (clicked)="openModal('lg')">Large</lib-button>
            </div>
          </div>
        </div>
      </section>

      <!-- Modal Templates -->
      <ng-template #basicModalTemplate>
        <lib-modal-container>
          <lib-modal-header>Basic Modal</lib-modal-header>
          <lib-modal-content>
            <p>This is a basic modal dialog with a title and close button.</p>
            <p>
              You can close it by clicking the X button, pressing ESC, or clicking the backdrop.
            </p>
          </lib-modal-content>
        </lib-modal-container>
      </ng-template>

      <ng-template #smallModalTemplate>
        <lib-modal-container>
          <lib-modal-header>Small Modal</lib-modal-header>
          <lib-modal-content>
            <p>This is a small modal (max-width: 384px).</p>
          </lib-modal-content>
        </lib-modal-container>
      </ng-template>

      <ng-template #mediumModalTemplate>
        <lib-modal-container>
          <lib-modal-header>Medium Modal</lib-modal-header>
          <lib-modal-content>
            <p>This is a medium modal (max-width: 512px).</p>
            <p>This is the default size.</p>
          </lib-modal-content>
        </lib-modal-container>
      </ng-template>

      <ng-template #largeModalTemplate>
        <lib-modal-container>
          <lib-modal-header>Large Modal</lib-modal-header>
          <lib-modal-content>
            <p>This is a large modal (max-width: 768px).</p>
            <p>It can contain more content and is useful for forms or detailed information.</p>
          </lib-modal-content>
          <lib-modal-footer>
            <lib-button variant="secondary" (clicked)="modal.close()">Cancel</lib-button>
            <lib-button variant="primary" (clicked)="modal.close()">Confirm</lib-button>
          </lib-modal-footer>
        </lib-modal-container>
      </ng-template>
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
})
export class Demo {
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  readonly loadingButton = signal(false);

  @ViewChild('basicModalTemplate') basicModalTemplate!: TemplateRef<any>;
  @ViewChild('smallModalTemplate') smallModalTemplate!: TemplateRef<any>;
  @ViewChild('mediumModalTemplate') mediumModalTemplate!: TemplateRef<any>;
  @ViewChild('largeModalTemplate') largeModalTemplate!: TemplateRef<any>;

  toggleLoading(): void {
    this.loadingButton.update((loading) => !loading);
    if (this.loadingButton()) {
      setTimeout(() => {
        this.loadingButton.set(false);
      }, 2000);
    }
  }

  openBasicModal(): void {
    this.modal.open(this.basicModalTemplate, this.viewContainerRef, {
      size: 'md',
      closable: true,
    });
  }

  openModal(size: 'sm' | 'md' | 'lg'): void {
    const templateMap = {
      sm: this.smallModalTemplate,
      md: this.mediumModalTemplate,
      lg: this.largeModalTemplate,
    };

    this.modal.open(templateMap[size], this.viewContainerRef, {
      size,
      closable: true,
    });
  }
}
