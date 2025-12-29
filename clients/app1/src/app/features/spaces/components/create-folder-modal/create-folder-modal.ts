import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  ViewContainerRef,
  effect,
  model,
} from '@angular/core';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input, Select, SelectOption } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { WorkspaceService } from '../../../../application/services/workspace.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-create-folder-modal',
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
      <lib-modal-header>{{ 'workspace.modals.createFolder' | translate }}</lib-modal-header>
      <lib-modal-content>
        <form class="create-folder-form" (ngSubmit)="handleSubmit()">
          <lib-input
            [label]="'workspace.modals.folderName' | translate"
            [placeholder]="'workspace.modals.folderNamePlaceholder' | translate"
            [(model)]="name"
            [required]="true"
            [errorMessage]="nameError()"
            [helperText]="'workspace.modals.folderNameHelper' | translate"
          />
          <div class="create-folder-form_field">
            <lib-select
              [label]="'workspace.modals.parentFolder' | translate"
              [options]="parentFolderOptions()"
              [(model)]="parentFolderModel"
              [placeholder]="'workspace.modals.parentFolderPlaceholder' | translate"
              [helperText]="'workspace.modals.parentFolderHelper' | translate"
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
          {{ 'workspace.modals.createFolder' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .create-folder-form {
        @apply flex flex-col gap-4;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CreateFolderModal {
  private readonly workspaceService = inject(WorkspaceService);
  private readonly organizationService = inject(OrganizationService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  readonly organizationId = input<string>();

  readonly name = signal('');
  readonly parentId = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  readonly parentFolderModel = model<string | null>(null);

  // Sync model signal with regular signal
  private readonly syncParentEffect = effect(() => {
    const selected = this.parentFolderModel();
    this.parentId.set(selected);
  });

  // Get folder tree for parent selector from workspace nodes
  readonly parentFolderOptions = computed<SelectOption<string | null>[]>(() => {
    const nodes = this.workspaceService.workspaceNodes();
    const options: SelectOption<string | null>[] = [
      {
        value: null,
        label: this.translateService.instant('workspace.modals.parentFolderPlaceholder'),
      },
    ];

    // Flatten workspace nodes recursively for parent selector (only folders, not spaces)
    const flattenFolders = (nodeList: any[], level = 0): void => {
      for (const node of nodeList) {
        // Only include folders (workspace nodes), not spaces
        if (node.type === 'folder') {
          const indent = '  '.repeat(level);
          options.push({
            value: node.id,
            label: `${indent}${node.title}`,
          });
          if (node.children && node.children.length > 0) {
            flattenFolders(node.children, level + 1);
          }
        } else if (node.type === 'space' && node.children && node.children.length > 0) {
          // For spaces, recurse into their children (pages) but don't include the space itself
          flattenFolders(node.children, level);
        }
      }
    };

    flattenFolders(nodes);

    return options;
  });

  readonly nameError = computed(() => {
    const value = this.name();
    if (!value.trim()) {
      return this.translateService.instant('workspace.modals.nameRequired');
    }
    if (value.trim().length < 3) {
      return this.translateService.instant('workspace.modals.nameMinLength');
    }
    return '';
  });

  readonly isValid = computed(() => {
    return !this.nameError() && this.name().trim() !== '';
  });

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    const orgId = this.organizationId() || this.organizationService.currentOrganization()?.id;
    if (!orgId) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      await this.workspaceService.createFolder({
        organizationId: orgId,
        title: this.name().trim(),
        parentId: this.parentId() || undefined,
      });

      this.toast.success(this.translateService.instant('workspace.modals.createFolderSuccess'));
      this.modal.close();
    } catch (error) {
      console.error('Failed to create folder:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('workspace.modals.createFolderError');
      this.toast.error(errorMessage);
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
