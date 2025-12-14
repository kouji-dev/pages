import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  effect,
  model,
} from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input, Select, SelectOption, ToastService } from 'shared-ui';
import { PageService, Page } from '../../application/services/page.service';
import { NavigationService } from '../../application/services/navigation.service';

@Component({
  selector: 'app-create-page-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input, Select],
  template: `
    <lib-modal-container>
      <lib-modal-header>Create Page</lib-modal-header>
      <lib-modal-content>
        <form class="create-page-form" (ngSubmit)="handleSubmit()">
          <lib-input
            label="Page Title"
            placeholder="Enter page title"
            [(model)]="title"
            [required]="true"
            [errorMessage]="titleError()"
            helperText="Choose a title for your page"
          />
          <div class="create-page-form_field">
            <lib-select
              label="Parent Page (optional)"
              [options]="parentPageOptions()"
              [(model)]="parentPageModel"
              [placeholder]="'None (root page)'"
              helperText="Select a parent page to create a child page"
            />
          </div>
        </form>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isSubmitting()">
          Cancel
        </lib-button>
        <lib-button
          variant="primary"
          (clicked)="handleSubmit()"
          [loading]="isSubmitting()"
          [disabled]="!isValid()"
        >
          Create Page
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .create-page-form {
        @apply flex flex-col gap-4;
      }

      .create-page-form_field {
        @apply flex flex-col gap-2;
      }

      .create-page-form_label {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CreatePageModal {
  private readonly pageService = inject(PageService);
  private readonly navigationService = inject(NavigationService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);

  readonly spaceId = input.required<string>();

  readonly title = signal('');
  readonly parentId = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  readonly parentPageModel = model<string | null>(null);

  // Sync model signal with regular signal
  private readonly syncParentEffect = effect(() => {
    this.parentId.set(this.parentPageModel());
  });

  readonly pageTree = computed(() => {
    const spaceId = this.spaceId();
    if (!spaceId) return [];
    return this.pageService.buildPageTree(spaceId);
  });

  readonly parentPageOptions = computed<SelectOption<string | null>[]>(() => {
    const tree = this.pageTree();
    const options: SelectOption<string | null>[] = [{ value: null, label: 'None (root page)' }];

    // Flatten page tree recursively for parent selector
    const flattenPages = (pageList: Page[], level = 0): void => {
      for (const page of pageList) {
        const indent = '  '.repeat(level);
        options.push({
          value: page.id,
          label: `${indent}${page.title}`,
        });
        if (page.children && page.children.length > 0) {
          flattenPages(page.children, level + 1);
        }
      }
    };

    flattenPages(tree);

    return options;
  });

  readonly titleError = computed(() => {
    const value = this.title();
    if (!value || value.trim() === '') {
      return 'Page title is required';
    }
    if (value.length > 255) {
      return 'Page title must be 255 characters or less';
    }
    return '';
  });

  readonly isValid = computed(() => {
    return !this.titleError() && this.title().trim() !== '';
  });

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    const spaceId = this.spaceId();
    if (!spaceId) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      const createdPage = await this.pageService.createPage({
        spaceId,
        title: this.title().trim(),
        content: undefined, // Content will be added later when editing the page
        parentId: this.parentId() || undefined,
      });

      this.toast.success('Page created successfully!');
      this.modal.close();

      // Navigate to the newly created page
      const organizationId = this.navigationService.currentOrganizationId();
      if (organizationId && createdPage.id) {
        this.navigationService.navigateToPage(organizationId, spaceId, createdPage.id);
      }
    } catch (error) {
      console.error('Failed to create page:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to create page. Please try again.';
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
