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
import { PageService, Page } from '../../../../application/services/page.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { SpaceService } from '../../../../application/services/space.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { CreateSpaceModal } from '../../../spaces/components/create-space-modal/create-space-modal';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { ViewContainerRef } from '@angular/core';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-create-page-modal',
  imports: [
    ModalContainer,
    ModalHeader,
    ModalContent,
    ModalFooter,
    Button,
    Input,
    Select,
    TranslatePipe,
  ],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{ 'pages.modals.createPage' | translate }}</lib-modal-header>
      <lib-modal-content>
        <form class="create-page-form" (ngSubmit)="handleSubmit()">
          @if (!spaceId()) {
            <div class="create-page-form_field">
              <lib-select
                [label]="'pages.modals.space' | translate"
                [options]="spaceOptions()"
                [(model)]="selectedSpaceModel"
                [placeholder]="'pages.modals.spacePlaceholder' | translate"
                [required]="true"
                [errorMessage]="spaceError()"
              />
              <lib-button
                variant="ghost"
                size="sm"
                leftIcon="plus"
                (clicked)="handleCreateSpace()"
                class="create-page-form_create-space-button"
              >
                {{ 'pages.modals.createNewSpace' | translate }}
              </lib-button>
            </div>
          }
          <lib-input
            [label]="'pages.modals.pageTitle' | translate"
            [placeholder]="'pages.modals.pageTitlePlaceholder' | translate"
            [(model)]="title"
            [required]="true"
            [errorMessage]="titleError()"
            [helperText]="'pages.modals.pageTitleHelper' | translate"
          />
          <div class="create-page-form_field">
            <lib-select
              [label]="'pages.modals.parentPage' | translate"
              [options]="parentPageOptions()"
              [(model)]="parentPageModel"
              [placeholder]="'pages.modals.parentPagePlaceholder' | translate"
              [helperText]="'pages.modals.parentPageHelper' | translate"
              [disabled]="!currentSpaceId()"
            />
          </div>
        </form>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isSubmitting()">
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button
          variant="primary"
          (clicked)="handleSubmit()"
          [loading]="isSubmitting()"
          [disabled]="!isValid()"
        >
          {{ 'pages.modals.createPage' | translate }}
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

      .create-page-form_create-space-button {
        @apply self-start;
      }

      .create-page-form_label {
        @apply text-sm font-medium;
        @apply text-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CreatePageModal {
  private readonly pageService = inject(PageService);
  private readonly navigationService = inject(NavigationService);
  private readonly spaceService = inject(SpaceService);
  private readonly organizationService = inject(OrganizationService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  readonly spaceId = input<string>();
  readonly organizationId = input<string>();

  readonly title = signal('');
  readonly parentId = signal<string | null>(null);
  readonly selectedSpaceId = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  readonly parentPageModel = model<string | null>(null);
  readonly selectedSpaceModel = model<string | null>(null);

  // Sync model signals with regular signals
  private readonly syncParentEffect = effect(() => {
    this.parentId.set(this.parentPageModel());
  });

  private readonly syncSpaceEffect = effect(() => {
    this.selectedSpaceId.set(this.selectedSpaceModel());
  });

  // Get current space ID (either from input or selected)
  readonly currentSpaceId = computed(() => {
    return this.spaceId() || this.selectedSpaceId();
  });

  // Load spaces when organizationId is provided
  readonly spaces = computed(() => {
    const orgId = this.organizationId();
    if (!orgId) return [];
    return this.spaceService.spacesList().filter((space) => space.organizationId === orgId);
  });

  readonly spaceOptions = computed<SelectOption<string>[]>(() => {
    return this.spaces().map((space) => ({
      value: space.id,
      label: space.name,
    }));
  });

  async handleCreateSpace(): Promise<void> {
    const orgId = this.organizationId() || this.organizationService.currentOrganization()?.id;
    if (!orgId) return;

    try {
      await firstValueFrom(
        this.modal.open(CreateSpaceModal, this.viewContainerRef, {
          size: 'md',
          data: { organizationId: orgId },
        }),
      );
      // Reload spaces after creating a new one
      this.spaceService.spaces.reload();
    } catch (error) {
      // Modal was closed/cancelled
    }
  }

  readonly spaceError = computed(() => {
    if (!this.spaceId() && !this.selectedSpaceId()) {
      return this.translateService.instant('pages.modals.spaceRequired');
    }
    return '';
  });

  readonly pageTree = computed(() => {
    const spaceId = this.currentSpaceId();
    if (!spaceId) return [];
    return this.pageService.buildPageTree(spaceId);
  });

  readonly parentPageOptions = computed<SelectOption<string | null>[]>(() => {
    const tree = this.pageTree();
    const options: SelectOption<string | null>[] = [
      { value: null, label: this.translateService.instant('pages.modals.parentPagePlaceholder') },
    ];

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
      return this.translateService.instant('pages.modals.titleRequired');
    }
    if (value.length > 255) {
      return this.translateService.instant('pages.modals.titleMaxLength');
    }
    return '';
  });

  readonly isValid = computed(() => {
    return (
      !this.titleError() &&
      !this.spaceError() &&
      this.title().trim() !== '' &&
      !!this.currentSpaceId()
    );
  });

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    const spaceId = this.currentSpaceId();
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

      this.toast.success(this.translateService.instant('pages.modals.createSuccess'));
      this.modal.close();

      // Navigate to the newly created page
      const organizationId = this.navigationService.currentOrganizationId();
      if (organizationId && createdPage.id) {
        this.navigationService.navigateToPage(organizationId, spaceId, createdPage.id);
      }
    } catch (error) {
      console.error('Failed to create page:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('pages.modals.createError');
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
