import { Component, signal, inject, ViewChild, TemplateRef, ViewContainerRef } from '@angular/core';
import {
  Button,
  Icon,
  Input,
  Spinner,
  Modal,
  ModalContainer,
  ModalHeader,
  ModalContent,
  ModalFooter,
  ToastService,
} from 'shared-ui';

@Component({
  selector: 'app-demo',
  imports: [Button, Icon, Input, Spinner, ModalContainer, ModalHeader, ModalContent, ModalFooter],
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

      <!-- Input Component Showcase -->
      <section class="demo_section">
        <h2 class="demo_section-title">Input Component</h2>

        <div class="demo_grid">
          <div class="demo_item">
            <h3 class="demo_item-title">Basic Input</h3>
            <div class="demo_item-content">
              <lib-input
                label="Name"
                placeholder="Enter your name"
                [(model)]="inputValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">With Helper Text</h3>
            <div class="demo_item-content">
              <lib-input
                label="Email"
                type="email"
                placeholder="example@email.com"
                helperText="We'll never share your email"
                [(model)]="emailValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">With Error Message</h3>
            <div class="demo_item-content">
              <lib-input
                label="Username"
                placeholder="Choose a username"
                errorMessage="Username is already taken"
                [(model)]="usernameValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Required Field</h3>
            <div class="demo_item-content">
              <lib-input
                label="Password"
                type="password"
                placeholder="Enter password"
                [required]="true"
                [(model)]="passwordValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Password with Toggle</h3>
            <div class="demo_item-content">
              <lib-input
                label="Password"
                type="password"
                placeholder="Enter password"
                [showPasswordToggle]="true"
                [(model)]="passwordToggleValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">With Icons</h3>
            <div class="demo_item-content">
              <lib-input
                label="Search"
                type="search"
                placeholder="Search..."
                leftIcon="search"
                [(model)]="searchValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Disabled Input</h3>
            <div class="demo_item-content">
              <lib-input
                label="Disabled Field"
                placeholder="Cannot edit this"
                [disabled]="true"
                [(model)]="disabledInputValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Readonly Input</h3>
            <div class="demo_item-content">
              <lib-input
                label="Readonly Field"
                [readonly]="true"
                [(model)]="readonlyInputValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Different Types</h3>
            <div class="demo_item-content">
              <lib-input
                label="Email"
                type="email"
                placeholder="email@example.com"
                [(model)]="typeEmailValue"
              ></lib-input>
              <lib-input
                label="Number"
                type="number"
                placeholder="Enter a number"
                [(model)]="typeNumberValue"
              ></lib-input>
              <lib-input
                label="URL"
                type="url"
                placeholder="https://example.com"
                [(model)]="typeUrlValue"
              ></lib-input>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Textarea</h3>
            <div class="demo_item-content">
              <lib-input
                label="Message"
                type="textarea"
                placeholder="Enter your message..."
                [rows]="4"
                helperText="Maximum 500 characters"
                [(model)]="textareaValue"
              ></lib-input>
              <lib-input
                label="Description"
                type="textarea"
                placeholder="Enter description"
                [rows]="6"
                [(model)]="textareaValue2"
              ></lib-input>
            </div>
          </div>
        </div>
      </section>

      <!-- Spinner Directive Showcase -->
      <section class="demo_section">
        <h2 class="demo_section-title">Loading Spinner Directive</h2>

        <div class="demo_grid">
          <div class="demo_item">
            <h3 class="demo_item-title">Basic Usage</h3>
            <div class="demo_item-content">
              <div
                *spinner="loadingBasic(); message: 'Loading...'"
                style="position: relative; padding: 2rem; border: 1px solid var(--color-border-default); border-radius: 0.5rem; min-height: 150px;"
              >
                <p>This content is wrapped with the spinner directive.</p>
                <p>When loading is true, a backdrop and spinner will appear.</p>
              </div>
              <lib-button (click)="loadingBasic.set(!loadingBasic())" style="margin-top: 1rem;">
                {{ loadingBasic() ? 'Stop Loading' : 'Start Loading' }}
              </lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Different Sizes</h3>
            <div class="demo_item-content">
              <div
                *spinner="loadingSmall(); size: 'sm'; message: 'Loading (small)...'"
                style="position: relative; padding: 2rem; border: 1px solid var(--color-border-default); border-radius: 0.5rem; min-height: 150px;"
              >
                <p>Small spinner (sm)</p>
              </div>
              <lib-button (click)="loadingSmall.set(!loadingSmall())" style="margin-top: 1rem;">
                Toggle Small
              </lib-button>

              <div
                *spinner="loadingMedium(); size: 'md'; message: 'Loading (medium)...'"
                style="position: relative; padding: 2rem; border: 1px solid var(--color-border-default); border-radius: 0.5rem; min-height: 150px; margin-top: 1rem;"
              >
                <p>Medium spinner (md)</p>
              </div>
              <lib-button (click)="loadingMedium.set(!loadingMedium())" style="margin-top: 1rem;">
                Toggle Medium
              </lib-button>

              <div
                *spinner="loadingLarge(); size: 'lg'; message: 'Loading (large)...'"
                style="position: relative; padding: 2rem; border: 1px solid var(--color-border-default); border-radius: 0.5rem; min-height: 150px; margin-top: 1rem;"
              >
                <p>Large spinner (lg)</p>
              </div>
              <lib-button (click)="loadingLarge.set(!loadingLarge())" style="margin-top: 1rem;">
                Toggle Large
              </lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Different Colors</h3>
            <div class="demo_item-content">
              <div
                *spinner="
                  loadingDefault();
                  color: 'default';
                  message: 'Loading with default color...'
                "
                style="position: relative; padding: 2rem; border: 1px solid var(--color-border-default); border-radius: 0.5rem; min-height: 150px;"
              >
                <p>Default color spinner</p>
              </div>
              <lib-button (click)="loadingDefault.set(!loadingDefault())" style="margin-top: 1rem;">
                Toggle Default
              </lib-button>

              <div
                *spinner="
                  loadingPrimary();
                  color: 'primary';
                  message: 'Loading with primary color...'
                "
                style="position: relative; padding: 2rem; border: 1px solid var(--color-border-default); border-radius: 0.5rem; min-height: 150px; margin-top: 1rem;"
              >
                <p>Primary color spinner</p>
              </div>
              <lib-button (click)="loadingPrimary.set(!loadingPrimary())" style="margin-top: 1rem;">
                Toggle Primary
              </lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">With Message</h3>
            <div class="demo_item-content">
              <div
                *spinner="loadingWithMessage(); message: 'Loading data...'"
                style="position: relative; padding: 2rem; border: 1px solid var(--color-border-default); border-radius: 0.5rem; min-height: 150px;"
              >
                <p>This example shows a spinner with a custom message.</p>
                <p>The message appears below the spinner.</p>
              </div>
              <lib-button
                (click)="loadingWithMessage.set(!loadingWithMessage())"
                style="margin-top: 1rem;"
              >
                {{ loadingWithMessage() ? 'Stop Loading' : 'Start Loading' }}
              </lib-button>
            </div>
          </div>

          <div class="demo_item">
            <h3 class="demo_item-title">Card with Spinner</h3>
            <div class="demo_item-content">
              <div
                *spinner="
                  loadingCard();
                  color: 'primary';
                  size: 'lg';
                  message: 'Loading card content...'
                "
                style="position: relative; padding: 2rem; background: var(--color-bg-secondary); border-radius: 0.5rem; min-height: 200px;"
              >
                <h4 style="margin-top: 0;">Card Title</h4>
                <p>This is a card component that can show a loading state.</p>
                <p>When loading, the entire card is covered with a backdrop.</p>
              </div>
              <lib-button (click)="loadingCard.set(!loadingCard())" style="margin-top: 1rem;">
                {{ loadingCard() ? 'Hide Spinner' : 'Show Spinner' }}
              </lib-button>
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
        @apply flex flex-col gap-3 items-start;
        width: 100%;
      }
    `,
  ],
})
export class Demo {
  readonly toast = inject(ToastService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  readonly loadingButton = signal(false);

  // Spinner directive demo states
  readonly loadingBasic = signal(false);
  readonly loadingSmall = signal(false);
  readonly loadingMedium = signal(false);
  readonly loadingLarge = signal(false);
  readonly loadingDefault = signal(false);
  readonly loadingPrimary = signal(false);
  readonly loadingWithMessage = signal(false);
  readonly loadingCard = signal(false);

  // Input demo values
  readonly inputValue = signal('');
  readonly emailValue = signal('');
  readonly usernameValue = signal('');
  readonly passwordValue = signal('');
  readonly passwordToggleValue = signal('');
  readonly searchValue = signal('');
  readonly typeEmailValue = signal('');
  readonly typeNumberValue = signal('');
  readonly typeUrlValue = signal('');
  readonly disabledInputValue = signal('Disabled value');
  readonly readonlyInputValue = signal('Read-only value');
  readonly textareaValue = signal('');
  readonly textareaValue2 = signal('');

  @ViewChild('basicModalTemplate') basicModalTemplate!: TemplateRef<any>;
  @ViewChild('smallModalTemplate') smallModalTemplate!: TemplateRef<any>;
  @ViewChild('mediumModalTemplate') mediumModalTemplate!: TemplateRef<any>;
  @ViewChild('largeModalTemplate') largeModalTemplate!: TemplateRef<any>;

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
