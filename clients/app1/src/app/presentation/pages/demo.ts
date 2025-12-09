import {
  Component,
  signal,
  inject,
  ViewChild,
  TemplateRef,
  ViewContainerRef,
  computed,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
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
  LoadingState,
  ErrorState,
  EmptyState,
  Dropdown,
  TextEditor,
  Sidenav,
  type SidenavItem,
} from 'shared-ui';
import { JsonPipe } from '@angular/common';

@Component({
  selector: 'app-demo',
  imports: [
    Button,
    Icon,
    Input,
    Spinner,
    ModalContainer,
    ModalHeader,
    ModalContent,
    ModalFooter,
    LoadingState,
    ErrorState,
    EmptyState,
    Dropdown,
    TextEditor,
    Sidenav,
    RouterLink,
    FormsModule,
    JsonPipe,
  ],
  template: `
    <div class="demo demo--with-sidenav">
      <div class="demo_content">
        <div class="demo_header">
          <a routerLink="/" class="demo_back-link">
            <lib-icon name="arrow-left" size="sm" />
            <span>Back to Home</span>
          </a>
          <h1 class="demo_title">Component Library Demo</h1>
          <p class="demo_subtitle">Showcasing shared-ui components</p>
        </div>

        <!-- Icon Component Showcase -->
        <section id="icon-component" class="demo_section">
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
        <section id="button-component" class="demo_section">
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
        <section id="input-component" class="demo_section">
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
        <section id="loading-spinner" class="demo_section">
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
                <lib-button
                  (click)="loadingDefault.set(!loadingDefault())"
                  style="margin-top: 1rem;"
                >
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
                <lib-button
                  (click)="loadingPrimary.set(!loadingPrimary())"
                  style="margin-top: 1rem;"
                >
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
        <section id="toast-component" class="demo_section">
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
                <lib-button (clicked)="showToastAtPosition('bottom-right')"
                  >Bottom Right</lib-button
                >
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

        <!-- Loading State Component Showcase -->
        <section id="loading-state" class="demo_section">
          <h2 class="demo_section-title">Loading State Component</h2>

          <div class="demo_grid">
            <div class="demo_item">
              <h3 class="demo_item-title">Basic Loading</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-loading-state />
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">With Message</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-loading-state message="Loading data..." />
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">Different Sizes</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-loading-state size="sm" message="Small spinner" />
                <lib-loading-state size="md" message="Medium spinner" />
                <lib-loading-state size="lg" message="Large spinner" />
              </div>
            </div>
          </div>
        </section>

        <!-- Error State Component Showcase -->
        <section id="error-state" class="demo_section">
          <h2 class="demo_section-title">Error State Component</h2>

          <div class="demo_grid">
            <div class="demo_item">
              <h3 class="demo_item-title">Basic Error</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-error-state />
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">With Custom Message</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-error-state
                  title="Connection Error"
                  message="Unable to connect to the server. Please check your internet connection."
                />
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">With Retry Action</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-error-state
                  title="Failed to Load"
                  message="Something went wrong while loading the data."
                  [retryLabel]="'Retry'"
                  (onRetry)="handleRetry()"
                />
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">Without Retry Button</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-error-state
                  title="Access Denied"
                  message="You don't have permission to view this content."
                  [showRetry]="false"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- Empty State Component Showcase -->
        <section id="empty-state" class="demo_section">
          <h2 class="demo_section-title">Empty State Component</h2>

          <div class="demo_grid">
            <div class="demo_item">
              <h3 class="demo_item-title">Basic Empty State</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-empty-state />
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">With Icon and Message</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-empty-state
                  title="No projects found"
                  message="Get started by creating your first project."
                  icon="folder"
                />
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">With Action Button</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-empty-state
                  title="No items yet"
                  message="Create your first item to get started."
                  icon="file-plus"
                  actionLabel="Create Item"
                  actionIcon="plus"
                  (onAction)="handleEmptyStateAction()"
                />
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">Different Variants</h3>
              <div
                class="demo_item-content"
                style="border: 1px solid var(--color-border-default); border-radius: 0.5rem; padding: 1rem;"
              >
                <lib-empty-state title="No tasks" actionLabel="Add Task" actionVariant="primary" />
                <lib-empty-state
                  title="No tasks"
                  actionLabel="Add Task"
                  actionVariant="secondary"
                  style="margin-top: 1rem;"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- Modal Component Showcase -->
        <section id="modal-component" class="demo_section">
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

        <!-- Dropdown Component Showcase -->
        <section id="dropdown-component" class="demo_section">
          <h2 class="demo_section-title">Dropdown Component</h2>

          <div class="demo_grid">
            <div class="demo_item">
              <h3 class="demo_item-title">Basic Dropdown (Click)</h3>
              <div class="demo_item-content">
                <button
                  type="button"
                  [libDropdown]="basicDropdownTemplate"
                  class="demo_dropdown-trigger"
                  #basicDropdown="libDropdown"
                >
                  Click me
                  <lib-icon
                    [name]="basicDropdown.open() ? 'chevron-up' : 'chevron-down'"
                    size="sm"
                  />
                </button>
                <ng-template #basicDropdownTemplate>
                  <div class="demo_dropdown-content">
                    <div class="demo_dropdown-item">Item 1</div>
                    <div class="demo_dropdown-item">Item 2</div>
                    <div class="demo_dropdown-item">Item 3</div>
                  </div>
                </ng-template>
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">Dropdown Positions</h3>
              <div class="demo_item-content" style="display: flex; gap: 1rem; flex-wrap: wrap;">
                <button
                  type="button"
                  [libDropdown]="positionDropdownTemplate"
                  [position]="'below'"
                  class="demo_dropdown-trigger"
                >
                  Below
                </button>
                <button
                  type="button"
                  [libDropdown]="positionDropdownTemplate"
                  [position]="'above'"
                  class="demo_dropdown-trigger"
                >
                  Above
                </button>
                <button
                  type="button"
                  [libDropdown]="positionDropdownTemplate"
                  [position]="'right'"
                  class="demo_dropdown-trigger"
                >
                  Right
                </button>
                <button
                  type="button"
                  [libDropdown]="positionDropdownTemplate"
                  [position]="'left'"
                  class="demo_dropdown-trigger"
                >
                  Left
                </button>
                <ng-template #positionDropdownTemplate>
                  <div class="demo_dropdown-content">
                    <div class="demo_dropdown-item">Menu Item 1</div>
                    <div class="demo_dropdown-item">Menu Item 2</div>
                    <div class="demo_dropdown-item">Menu Item 3</div>
                  </div>
                </ng-template>
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">With Icons</h3>
              <div class="demo_item-content">
                <button
                  type="button"
                  [libDropdown]="iconDropdownTemplate"
                  class="demo_dropdown-trigger"
                  #iconDropdown="libDropdown"
                >
                  Actions
                  <lib-icon
                    [name]="iconDropdown.open() ? 'chevron-up' : 'chevron-down'"
                    size="sm"
                  />
                </button>
                <ng-template #iconDropdownTemplate>
                  <div class="demo_dropdown-content">
                    <div class="demo_dropdown-item">
                      <lib-icon name="pencil" size="sm" />
                      <span>Edit</span>
                    </div>
                    <div class="demo_dropdown-item">
                      <lib-icon name="copy" size="sm" />
                      <span>Copy</span>
                    </div>
                    <div class="demo_dropdown-item">
                      <lib-icon name="trash" size="sm" />
                      <span>Delete</span>
                    </div>
                  </div>
                </ng-template>
              </div>
            </div>

            <div class="demo_item">
              <h3 class="demo_item-title">With Data Binding</h3>
              <div class="demo_item-content">
                <button
                  type="button"
                  [libDropdown]="dataDropdownTemplate"
                  [dropdownData]="selectedItem()"
                  class="demo_dropdown-trigger"
                  #dataDropdown="libDropdown"
                >
                  Selected: {{ selectedItem() || 'None' }}
                  <lib-icon
                    [name]="dataDropdown.open() ? 'chevron-up' : 'chevron-down'"
                    size="sm"
                  />
                </button>
                <ng-template #dataDropdownTemplate let-data>
                  <div class="demo_dropdown-content">
                    @for (item of dropdownItems(); track item) {
                      <div
                        class="demo_dropdown-item"
                        [class.demo_dropdown-item--active]="selectedItem() === item"
                        (click)="selectItem(item, dataDropdown)"
                      >
                        {{ item }}
                      </div>
                    }
                  </div>
                </ng-template>
              </div>
            </div>
          </div>
        </section>

        <!-- Text Editor Component Showcase -->
        <section id="text-editor" class="demo_section">
          <h2 class="demo_section-title">Text Editor Component (Lexical)</h2>
          <p
            class="demo_section-description"
            style="margin-bottom: 2rem; color: var(--color-text-secondary);"
          >
            A powerful rich text editor built with Lexical. Supports formatting, headings, lists,
            links, quotes, font sizes, and more. Use the controls below to toggle between different
            states and see all formatting options.
          </p>

          <div class="demo_grid">
            <div class="demo_item" style="grid-column: 1 / -1;">
              <h3 class="demo_item-title">Interactive Text Editor</h3>
              <p
                class="demo_item-description"
                style="font-size: 0.875rem; color: var(--color-text-secondary); margin-bottom: 1rem;"
              >
                Fully-featured editor with controls to toggle states, load formatted content, and
                view HTML output.
              </p>
              <div class="demo_item-content">
                <!-- Controls -->
                <div
                  style="margin-bottom: 1rem; padding: 1rem; background: var(--color-bg-secondary); border-radius: 0.5rem; display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center;"
                >
                  <lib-button
                    variant="primary"
                    size="sm"
                    (clicked)="editorDisabled.set(!editorDisabled())"
                  >
                    {{ editorDisabled() ? 'Enable Editor' : 'Disable Editor' }}
                  </lib-button>
                  <lib-button
                    variant="secondary"
                    size="sm"
                    (clicked)="editorReadOnly.set(!editorReadOnly())"
                  >
                    {{ editorReadOnly() ? 'Make Editable' : 'Make Read-Only' }}
                  </lib-button>
                  <lib-button variant="ghost" size="sm" (clicked)="loadFormattedContent()">
                    Load Formatted Example
                  </lib-button>
                  <lib-button variant="ghost" size="sm" (clicked)="clearEditor()">
                    Clear Content
                  </lib-button>
                  <lib-button variant="ghost" size="sm" (clicked)="showToolbar.set(!showToolbar())">
                    {{ showToolbar() ? 'Hide Toolbar' : 'Show Toolbar' }}
                  </lib-button>
                  <span
                    style="margin-left: auto; display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--color-text-secondary);"
                  >
                    <strong>Status:</strong>
                    <span
                      [style.color]="
                        editorDisabled()
                          ? 'var(--color-error)'
                          : editorReadOnly()
                            ? 'var(--color-warning)'
                            : 'var(--color-success)'
                      "
                    >
                      {{
                        editorDisabled() ? 'Disabled' : editorReadOnly() ? 'Read-Only' : 'Editable'
                      }}
                    </span>
                  </span>
                </div>

                <!-- Editor -->
                <lib-text-editor
                  [placeholder]="
                    editorDisabled()
                      ? 'Editor is disabled'
                      : editorReadOnly()
                        ? 'Editor is read-only'
                        : 'Start typing... Use the toolbar to format your text.'
                  "
                  [showToolbar]="showToolbar()"
                  [disabled]="editorDisabled()"
                  [readOnly]="editorReadOnly()"
                  [initialValue]="editorInitialValue()"
                  (htmlChange)="editorHtml.set($event)"
                  (valueChange)="editorText.set($event)"
                />

                <!-- HTML Output -->
                <div
                  style="margin-top: 1rem; padding: 1rem; background: var(--color-bg-secondary); border-radius: 0.5rem;"
                >
                  <div
                    style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;"
                  >
                    <p style="font-size: 0.875rem; color: var(--color-text-secondary); margin: 0;">
                      HTML Output:
                    </p>
                    <lib-button
                      variant="ghost"
                      size="sm"
                      (clicked)="showHtmlOutput.set(!showHtmlOutput())"
                    >
                      {{ showHtmlOutput() ? 'Hide' : 'Show' }} HTML
                    </lib-button>
                  </div>
                  @if (showHtmlOutput()) {
                    <pre
                      style="font-size: 0.75rem; overflow-x: auto; max-height: 200px; overflow-y: auto; margin: 0; padding: 0.5rem; background: var(--color-bg-primary); border-radius: 0.25rem;"
                      >{{ editorHtml() || '(empty)' }}</pre
                    >
                  }
                </div>

                <!-- Rendered Output -->
                <div
                  style="margin-top: 1rem; padding: 1rem; border: 1px solid var(--color-border-default); border-radius: 0.5rem; min-height: 150px;"
                >
                  <div
                    style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;"
                  >
                    <p style="font-size: 0.875rem; color: var(--color-text-secondary); margin: 0;">
                      Rendered Output:
                    </p>
                    <lib-button
                      variant="ghost"
                      size="sm"
                      (clicked)="showRenderedOutput.set(!showRenderedOutput())"
                    >
                      {{ showRenderedOutput() ? 'Hide' : 'Show' }} Preview
                    </lib-button>
                  </div>
                  @if (showRenderedOutput()) {
                    @if (editorHtml()) {
                      <div [innerHTML]="editorHtml()"></div>
                    } @else {
                      <p style="color: var(--color-text-secondary); font-style: italic; margin: 0;">
                        Type in the editor above to see rendered output here.
                      </p>
                    }
                  }
                </div>
              </div>
            </div>

            <div class="demo_item" style="grid-column: 1 / -1;">
              <h3 class="demo_item-title">Form Integration Example</h3>
              <p
                class="demo_item-description"
                style="font-size: 0.875rem; color: var(--color-text-secondary); margin-bottom: 1rem;"
              >
                Editor integrated with Angular forms using ngModel. The value is bound and can be
                submitted.
              </p>
              <div class="demo_item-content">
                <form
                  (ngSubmit)="onFormSubmit()"
                  style="display: flex; flex-direction: column; gap: 1rem;"
                >
                  <lib-input label="Title" placeholder="Enter a title" [(model)]="formTitle" />
                  <div>
                    <label
                      style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; color: var(--color-text-primary);"
                    >
                      Content
                    </label>
                    <lib-text-editor
                      placeholder="Enter your content here..."
                      [showToolbar]="true"
                      [(ngModel)]="formContent"
                      name="content"
                    />
                  </div>
                  <div style="display: flex; gap: 0.5rem;">
                    <lib-button type="submit" variant="primary">Submit Form</lib-button>
                    <lib-button type="button" variant="secondary" (clicked)="resetForm()"
                      >Reset</lib-button
                    >
                  </div>
                </form>
                @if (formSubmitted()) {
                  <div
                    style="margin-top: 1rem; padding: 1rem; background: var(--color-bg-secondary); border-radius: 0.5rem;"
                  >
                    <p
                      style="font-size: 0.875rem; color: var(--color-text-secondary); margin-bottom: 0.5rem;"
                    >
                      Form Data:
                    </p>
                    <pre style="font-size: 0.75rem; overflow-x: auto;">{{ formData() | json }}</pre>
                  </div>
                }
              </div>
            </div>
          </div>
        </section>
      </div>
      <lib-sidenav [title]="'Components'" [items]="sidenavItems" />
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .demo {
        @apply w-full;
        padding: 2rem;
      }

      .demo--with-sidenav {
        @apply pr-72;
      }

      .demo_content {
        @apply max-w-7xl;
        @apply mx-auto;
      }

      .demo_header {
        @apply mb-8;
      }

      .demo_back-link {
        @apply inline-flex items-center gap-2;
        @apply text-sm font-medium;
        @apply mb-4;
        @apply text-primary-500;
        text-decoration: none;
        @apply transition-colors;
        @apply hover:opacity-80;
      }

      .demo_back-link:hover {
        @apply text-primary-600;
      }

      .demo_title {
        @apply text-4xl font-bold mb-2;
        @apply text-text-primary;
      }

      .demo_subtitle {
        @apply text-lg mb-8;
        @apply text-text-secondary;
      }

      .demo_section {
        @apply mb-12;
      }

      .demo_section-title {
        @apply text-2xl font-semibold mb-6;
        @apply text-text-primary;
      }

      .demo_grid {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
      }

      .demo_item {
        @apply flex flex-col;
      }

      .demo_item-title {
        @apply text-lg font-medium mb-3;
        @apply text-text-primary;
      }

      .demo_item-content {
        @apply flex flex-col gap-3 items-start;
        width: 100%;
      }

      .demo_dropdown-trigger {
        @apply flex items-center gap-2;
        @apply px-4 py-2;
        @apply rounded-md;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
        @apply text-text-primary;
        @apply font-medium;
        @apply transition-colors;
        @apply cursor-pointer;
        @apply hover:bg-gray-100;
      }

      .demo_dropdown-content {
        @apply py-1;
        min-width: 12rem;
      }

      .demo_dropdown-item {
        @apply flex items-center gap-2;
        @apply px-4 py-2;
        @apply text-sm;
        @apply transition-colors;
        @apply text-text-primary;
        @apply cursor-pointer;
        @apply hover:bg-gray-100;
      }

      .demo_dropdown-item--active {
        @apply bg-bg-secondary;
        @apply text-primary-500;
        font-weight: 500;
      }

      .demo_dropdown-item lib-icon {
        @apply flex-shrink-0;
      }
    `,
  ],
})
export class Demo {
  readonly toast = inject(ToastService);
  readonly modal = inject(Modal);

  readonly sidenavItems: SidenavItem[] = [
    { label: 'Icon Component', anchor: 'icon-component' },
    { label: 'Button Component', anchor: 'button-component' },
    { label: 'Input Component', anchor: 'input-component' },
    { label: 'Loading Spinner', anchor: 'loading-spinner' },
    { label: 'Toast Component', anchor: 'toast-component' },
    { label: 'Loading State', anchor: 'loading-state' },
    { label: 'Error State', anchor: 'error-state' },
    { label: 'Empty State', anchor: 'empty-state' },
    { label: 'Modal Component', anchor: 'modal-component' },
    { label: 'Dropdown Component', anchor: 'dropdown-component' },
    { label: 'Text Editor', anchor: 'text-editor' },
  ];
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

  // Dropdown demo values
  readonly selectedItem = signal<string | null>(null);
  readonly dropdownItems = signal(['Option 1', 'Option 2', 'Option 3', 'Option 4']);
  readonly textareaValue = signal('');
  readonly textareaValue2 = signal('');

  // Text Editor demo values
  readonly editorHtml = signal('');
  readonly editorText = signal('');
  readonly editorDisabled = signal(false);
  readonly editorReadOnly = signal(false);
  readonly showToolbar = signal(true);
  readonly showHtmlOutput = signal(true);
  readonly showRenderedOutput = signal(true);
  readonly editorInitialValue = signal<string | undefined>(undefined);

  // Form integration
  readonly formTitle = signal('');
  readonly formContent = signal('');
  readonly formSubmitted = signal(false);
  readonly formData = computed(() => ({
    title: this.formTitle(),
    content: this.formContent(),
  }));

  // Formatted content example
  readonly formattedContentExample = `
    <h1>Welcome to the Text Editor</h1>
    <p>This is a <strong>rich text editor</strong> built with <em>Lexical</em>.</p>
    <h2>Features</h2>
    <ul>
      <li><strong>Bold</strong>, <em>italic</em>, <u>underline</u>, <s>strikethrough</s>, and <code>code</code> text</li>
      <li>Headings (H1, H2, H3)</li>
      <li>Ordered and unordered lists</li>
      <li>Links with modal input</li>
      <li>Block quotes</li>
      <li>Font sizes (XS, SM, MD, LG, XL)</li>
      <li>Undo/Redo support</li>
    </ul>
    <h3>Formatting Examples</h3>
    <p>This paragraph demonstrates various <strong>text styles</strong> including <em>italic</em>, <u>underline</u>, <s>strikethrough</s>, and <code>inline code</code>.</p>
    <ol>
      <li>Ordered list item 1</li>
      <li>Ordered list item 2</li>
      <li>Ordered list item 3</li>
    </ol>
    <blockquote>This is a block quote. It can contain multiple paragraphs and other formatting. Block quotes are great for highlighting important information.</blockquote>
    <p>Here's a <a href="https://lexical.dev" target="_blank">link to Lexical</a> to learn more about the editor framework.</p>
    <p style="font-size: var(--text-xs);">Extra small text (XS)</p>
    <p style="font-size: var(--text-sm);">Small text (SM)</p>
    <p style="font-size: var(--text-md);">Medium text (MD - default)</p>
    <p style="font-size: var(--text-lg);">Large text (LG)</p>
    <p style="font-size: var(--text-xl);">Extra large text (XL)</p>
  `;

  loadFormattedContent(): void {
    this.editorInitialValue.set(this.formattedContentExample);
    this.toast.info('Formatted content loaded');
  }

  clearEditor(): void {
    this.editorInitialValue.set('');
    this.editorHtml.set('');
    this.editorText.set('');
    this.toast.info('Editor cleared');
  }

  onFormSubmit(): void {
    this.formSubmitted.set(true);
    this.toast.success('Form submitted successfully!');
  }

  resetForm(): void {
    this.formTitle.set('');
    this.formContent.set('');
    this.formSubmitted.set(false);
    this.toast.info('Form reset');
  }

  @ViewChild('basicModalTemplate') basicModalTemplate!: TemplateRef<any>;
  @ViewChild('smallModalTemplate') smallModalTemplate!: TemplateRef<any>;
  @ViewChild('mediumModalTemplate') mediumModalTemplate!: TemplateRef<any>;
  @ViewChild('largeModalTemplate') largeModalTemplate!: TemplateRef<any>;
  @ViewChild('basicDropdownTemplate') basicDropdownTemplate!: TemplateRef<any>;
  @ViewChild('positionDropdownTemplate') positionDropdownTemplate!: TemplateRef<any>;
  @ViewChild('iconDropdownTemplate') iconDropdownTemplate!: TemplateRef<any>;
  @ViewChild('dataDropdownTemplate') dataDropdownTemplate!: TemplateRef<any>;

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

  handleRetry(): void {
    this.toast.success('Retry action triggered!');
  }

  handleEmptyStateAction(): void {
    this.toast.info('Action button clicked!');
  }

  selectItem(item: string, dropdown: Dropdown): void {
    this.selectedItem.set(item);
    dropdown.open.set(false);
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
