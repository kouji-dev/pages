import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  ViewContainerRef,
} from '@angular/core';
import { Button, LoadingState, ErrorState, EmptyState, Modal, Input } from 'shared-ui';
import { TranslatePipe } from '@ngx-translate/core';
import { SpaceService, Space } from '../../../../application/services/space.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { SpaceCard } from '../../components/space-card/space-card';
import { CreateSpaceModal } from '../../components/create-space-modal/create-space-modal';

@Component({
  selector: 'app-spaces-page',
  imports: [Button, LoadingState, ErrorState, EmptyState, SpaceCard, Input, TranslatePipe],
  template: `
    <div class="spaces-page">
      <div class="spaces-page_header">
        <div class="spaces-page_header-content">
          <div>
            <h1 class="spaces-page_title">{{ 'spaces.title' | translate }}</h1>
            <p class="spaces-page_subtitle">{{ 'spaces.subtitle' | translate }}</p>
          </div>
          <lib-button
            variant="primary"
            size="md"
            leftIcon="plus"
            (clicked)="handleCreateSpace()"
            [disabled]="!organizationId()"
          >
            {{ 'spaces.createSpace' | translate }}
          </lib-button>
        </div>
      </div>

      <div class="spaces-page_content">
        @if (!organizationId()) {
          <lib-empty-state
            [title]="'spaces.noOrganizationSelected' | translate"
            [message]="'spaces.noOrganizationSelectedDescription' | translate"
            icon="building"
            [actionLabel]="'spaces.goToOrganizations' | translate"
            actionIcon="arrow-right"
            (onAction)="handleGoToOrganizations()"
          />
        } @else if (spaceService.isLoading()) {
          <lib-loading-state [message]="'spaces.loadingSpaces' | translate" />
        } @else if (spaceService.hasError()) {
          <lib-error-state
            [title]="'spaces.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else {
          <div class="spaces-page_search">
            <lib-input
              [placeholder]="'spaces.searchPlaceholder' | translate"
              [(model)]="spaceService.searchQuery"
              leftIcon="search"
              class="spaces-page_search-input"
            />
          </div>
          @if (allSpaces().length === 0) {
            @if (spaceService.searchQuery().trim()) {
              <lib-empty-state
                [title]="'spaces.noSpacesFound' | translate"
                [message]="'spaces.noSpacesFoundDescription' | translate"
                icon="search"
              />
            } @else {
              <lib-empty-state
                [title]="'spaces.noSpaces' | translate"
                [message]="'spaces.noSpacesDescription' | translate"
                icon="book"
                [actionLabel]="'spaces.createSpace' | translate"
                actionIcon="plus"
                (onAction)="handleCreateSpace()"
              />
            }
          } @else {
            <div class="spaces-page_grid">
              @for (space of allSpaces(); track space.id) {
                <app-space-card [space]="space" (onSettings)="handleSpaceSettings($event)" />
              }
            </div>
          }
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .spaces-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-background;
      }

      .spaces-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border;
      }

      .spaces-page_header-content {
        @apply max-w-7xl mx-auto;
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .spaces-page_title {
        @apply text-3xl font-bold;
        @apply text-foreground;
        margin: 0 0 0.5rem 0;
      }

      .spaces-page_subtitle {
        @apply text-base;
        @apply text-muted-foreground;
        margin: 0;
      }

      .spaces-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .spaces-page_search {
        @apply max-w-7xl mx-auto;
        @apply mb-6;
      }

      .spaces-page_search-input {
        @apply max-w-md;
      }

      .spaces-page_grid {
        @apply max-w-7xl mx-auto;
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3;
        @apply gap-6;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SpacesPage {
  readonly spaceService = inject(SpaceService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId();
  });

  readonly allSpaces = computed(() => {
    const orgId = this.organizationId();
    if (!orgId) return [];
    return this.spaceService.getSpacesByOrganization(orgId);
  });

  readonly errorMessage = computed(() => {
    const error = this.spaceService.error();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading spaces.';
    }
    return 'An unknown error occurred.';
  });

  handleCreateSpace(): void {
    const orgId = this.organizationId();
    if (!orgId) {
      return;
    }
    this.modal.open(CreateSpaceModal, this.viewContainerRef, {
      size: 'md',
      data: { organizationId: orgId },
    });
  }

  handleSpaceSettings(space: Space): void {
    const orgId = this.organizationId();
    if (orgId) {
      this.navigationService.navigateToSpaceSettings(orgId, space.id);
    }
  }

  handleRetry(): void {
    this.spaceService.spaces.reload();
  }

  handleGoToOrganizations(): void {
    this.navigationService.navigateToOrganizations();
  }
}
