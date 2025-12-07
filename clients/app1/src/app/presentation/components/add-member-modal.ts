import { Component, ChangeDetectionStrategy, signal, computed, inject, input } from '@angular/core';
import {
  Modal,
  ModalContainer,
  ModalHeader,
  ModalContent,
  ModalFooter,
  Button,
  Input,
  Icon,
} from 'shared-ui';
import { ToastService } from 'shared-ui';
import {
  OrganizationMembersService,
  AddMemberRequest,
} from '../../application/services/organization-members.service';
import { UserService, User } from '../../application/services/user.service';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';

@Component({
  selector: 'app-add-member-modal',
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input, Icon],
  template: `
    <lib-modal-container>
      <lib-modal-header>Add Member</lib-modal-header>
      <lib-modal-content>
        <form class="add-member-form" (ngSubmit)="handleSubmit()">
          <div class="add-member-form_search">
            <lib-input
              label="Search Users"
              placeholder="Search by name or email..."
              [(model)]="searchQuery"
              leftIcon="search"
              (input)="onSearchInput()"
            />
            @if (userService.isLoading()) {
              <div class="add-member-form_loading">
                <lib-icon name="loader" size="sm" animation="spin" />
                <span>Searching...</span>
              </div>
            }
          </div>

          @if (searchQuery().trim().length >= 2) {
            <div class="add-member-form_results">
              @if (userService.hasError()) {
                <div class="add-member-form_error">
                  <lib-icon name="circle-alert" size="sm" />
                  <span>Failed to search users. Please try again.</span>
                </div>
              } @else if (users().length === 0 && !userService.isLoading()) {
                <div class="add-member-form_empty">
                  <lib-icon name="search" size="sm" />
                  <span>No users found. Try a different search query.</span>
                </div>
              } @else {
                <div class="add-member-form_user-list">
                  @for (user of users(); track user.id) {
                    <button
                      type="button"
                      class="add-member-form_user-item"
                      [class.add-member-form_user-item--selected]="selectedUserId() === user.id"
                      (click)="selectUser(user)"
                    >
                      <div class="add-member-form_user-avatar">
                        @if (user.avatar_url) {
                          <img
                            [src]="user.avatar_url"
                            [alt]="user.name"
                            class="add-member-form_user-avatar-image"
                          />
                        } @else {
                          <div class="add-member-form_user-avatar-placeholder">
                            {{ getInitials(user.name) }}
                          </div>
                        }
                      </div>
                      <div class="add-member-form_user-info">
                        <div class="add-member-form_user-name">{{ user.name }}</div>
                        <div class="add-member-form_user-email">{{ user.email }}</div>
                      </div>
                      @if (selectedUserId() === user.id) {
                        <lib-icon name="check" size="sm" class="add-member-form_user-check" />
                      }
                    </button>
                  }
                </div>
              }
            </div>
          } @else {
            <div class="add-member-form_hint">
              <lib-icon name="info" size="sm" />
              <span>Enter at least 2 characters to search for users.</span>
            </div>
          }

          @if (selectedUserId()) {
            <div class="add-member-form_role">
              <label class="add-member-form_role-label">Role</label>
              <div class="add-member-form_role-options">
                @for (role of availableRoles(); track role.value) {
                  <button
                    type="button"
                    class="add-member-form_role-option"
                    [class.add-member-form_role-option--selected]="selectedRole() === role.value"
                    (click)="selectedRole.set(role.value)"
                  >
                    <div class="add-member-form_role-option-header">
                      <span class="add-member-form_role-option-name">{{ role.label }}</span>
                    </div>
                    <p class="add-member-form_role-option-description">{{ role.description }}</p>
                  </button>
                }
              </div>
            </div>
          }
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
          Add Member
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .add-member-form {
        @apply flex flex-col;
        @apply gap-4;
      }

      .add-member-form_search {
        @apply flex flex-col;
        @apply gap-2;
      }

      .add-member-form_loading {
        @apply flex items-center gap-2;
        @apply text-sm;
        color: var(--color-text-secondary);
      }

      .add-member-form_results {
        @apply flex flex-col;
        @apply gap-2;
        max-height: 300px;
        @apply overflow-y-auto;
      }

      .add-member-form_error {
        @apply flex items-center gap-2;
        @apply p-3;
        @apply rounded-lg;
        @apply text-sm;
        background: var(--color-error-50);
        color: var(--color-error);
      }

      .add-member-form_empty {
        @apply flex items-center gap-2;
        @apply p-3;
        @apply text-sm;
        color: var(--color-text-secondary);
      }

      .add-member-form_user-list {
        @apply flex flex-col;
        @apply gap-1;
      }

      .add-member-form_user-item {
        @apply flex items-center gap-3;
        @apply w-full;
        @apply p-3;
        @apply rounded-lg;
        @apply border;
        border-color: var(--color-border-default);
        background: var(--color-bg-primary);
        @apply transition-colors;
        @apply cursor-pointer;
        @apply hover:bg-gray-50;
        text-align: left;
      }

      .add-member-form_user-item--selected {
        border-color: var(--color-primary-500);
        background: var(--color-primary-50);
      }

      .add-member-form_user-avatar {
        @apply w-10 h-10;
        @apply rounded-full;
        @apply overflow-hidden;
        @apply flex-shrink-0;
        background: var(--color-bg-tertiary);
      }

      .add-member-form_user-avatar-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .add-member-form_user-avatar-placeholder {
        @apply w-full h-full;
        @apply flex items-center justify-center;
        @apply text-sm font-semibold;
        color: var(--color-text-primary);
      }

      .add-member-form_user-info {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-w-0;
      }

      .add-member-form_user-name {
        @apply text-sm font-medium;
        color: var(--color-text-primary);
        @apply truncate;
      }

      .add-member-form_user-email {
        @apply text-xs;
        color: var(--color-text-secondary);
        @apply truncate;
      }

      .add-member-form_user-check {
        @apply flex-shrink-0;
        color: var(--color-primary-500);
      }

      .add-member-form_hint {
        @apply flex items-center gap-2;
        @apply p-3;
        @apply text-sm;
        color: var(--color-text-secondary);
      }

      .add-member-form_role {
        @apply flex flex-col;
        @apply gap-3;
        @apply pt-4;
        @apply border-t;
        border-color: var(--color-border-default);
      }

      .add-member-form_role-label {
        @apply text-sm font-medium;
        color: var(--color-text-primary);
      }

      .add-member-form_role-options {
        @apply grid grid-cols-1 gap-2;
      }

      .add-member-form_role-option {
        @apply flex flex-col;
        @apply gap-1;
        @apply p-3;
        @apply rounded-lg;
        @apply border;
        border-color: var(--color-border-default);
        background: var(--color-bg-primary);
        @apply transition-colors;
        @apply cursor-pointer;
        @apply hover:bg-gray-50;
        text-align: left;
      }

      .add-member-form_role-option--selected {
        border-color: var(--color-primary-500);
        background: var(--color-primary-50);
      }

      .add-member-form_role-option-header {
        @apply flex items-center justify-between;
      }

      .add-member-form_role-option-name {
        @apply text-sm font-medium;
        color: var(--color-text-primary);
      }

      .add-member-form_role-option-description {
        @apply text-xs;
        color: var(--color-text-secondary);
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddMemberModal {
  private readonly modal = inject(Modal);
  private readonly membersService = inject(OrganizationMembersService);
  readonly userService = inject(UserService);
  private readonly toast = inject(ToastService);

  readonly organizationId = input.required<string>();
  readonly searchQuery = signal('');
  readonly selectedUserId = signal<string | null>(null);
  readonly selectedRole = signal<'admin' | 'member' | 'viewer'>('member');
  readonly isSubmitting = signal(false);

  private readonly searchSubject = new Subject<string>();

  readonly users = computed(() => this.userService.users());

  readonly availableRoles = computed(() => [
    {
      value: 'admin' as const,
      label: 'Admin',
      description: 'Full access to manage organization and members',
    },
    {
      value: 'member' as const,
      label: 'Member',
      description: 'Can create and edit projects, but cannot manage members',
    },
    {
      value: 'viewer' as const,
      label: 'Viewer',
      description: 'Read-only access to organization content',
    },
  ]);

  readonly isValid = computed(() => {
    return this.selectedUserId() !== null && !this.isSubmitting();
  });

  constructor() {
    // Debounce search input
    this.searchSubject.pipe(debounceTime(300), distinctUntilChanged()).subscribe((query) => {
      if (query.trim().length >= 2) {
        this.userService.searchUsers(query.trim());
      }
    });
  }

  getInitials(name: string): string {
    const nameParts = name.split(' ');
    const initials = nameParts
      .map((part) => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
    return initials || 'U';
  }

  onSearchInput(): void {
    this.searchSubject.next(this.searchQuery());
  }

  selectUser(user: User): void {
    this.selectedUserId.set(user.id);
  }

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    const userId = this.selectedUserId();
    if (!userId) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      const request: AddMemberRequest = {
        user_id: userId,
        role: this.selectedRole(),
      };

      await this.membersService.addMember(this.organizationId()!, request);
      this.toast.success('Member added successfully!');
      this.modal.close({ success: true });
    } catch (error) {
      console.error('Failed to add member:', error);
      this.toast.error('Failed to add member. Please try again.');
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
