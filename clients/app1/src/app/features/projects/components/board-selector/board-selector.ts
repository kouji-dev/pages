import { ChangeDetectionStrategy, Component, computed, input, model, output } from '@angular/core';
import { Button, Dropdown, Input, Icon, Badge } from 'shared-ui';
import { TranslatePipe } from '@ngx-translate/core';
import { BoardResponse } from '../../../../application/services/board.service';

@Component({
  selector: 'app-board-selector',
  standalone: true,
  imports: [Button, Dropdown, Input, Icon, Badge, TranslatePipe],
  template: `
    <lib-button
      variant="outline"
      size="sm"
      [libDropdown]="dropdownTemplate"
      [position]="'below'"
      [containerClass]="'lib-dropdown-panel--fit-content'"
      class="board-selector_button"
      #dropdown="libDropdown"
    >
      <div class="board-selector_button-content">
        <span class="board-selector_current-name">{{ selectedBoardName() }}</span>
        <lib-icon name="chevron-down" size="sm" class="board-selector_chevron" />
      </div>
    </lib-button>

    <ng-template #dropdownTemplate>
      <div class="board-selector_dropdown">
        <div class="board-selector_actions">
          <lib-button
            variant="ghost"
            size="sm"
            leftIcon="plus"
            fullWidth
            class="board-selector_create"
            (clicked)="handleCreateBoard(dropdown)"
          >
            {{ 'common.create' | translate }}
          </lib-button>
          <lib-button
            variant="ghost"
            size="sm"
            leftIcon="layers"
            fullWidth
            class="board-selector_create"
            (clicked)="handleCreateGroupBoard(dropdown)"
          >
            Create Group Board
          </lib-button>
        </div>

        <div class="board-selector_search">
          <lib-input
            [placeholder]="'common.search' | translate"
            [(model)]="searchQuery"
            leftIcon="search"
          />
        </div>

        <div class="board-selector_list">
          @if (filteredBoards().length === 0) {
            <div class="board-selector_empty">{{ 'common.noResults' | translate }}</div>
          } @else {
            @for (board of filteredBoards(); track board.id) {
              <button
                type="button"
                class="board-selector_item"
                [class.board-selector_item--active]="board.id === selectedBoardId()"
                (click)="handleSelectBoard(board.id, dropdown)"
              >
                <div class="board-selector_item-main">
                  <span class="board-selector_item-name">{{ board.name }}</span>
                  @if (board.board_type === 'group') {
                    <lib-badge variant="info" class="board-selector_type-badge">Group</lib-badge>
                  }
                  @if (board.is_default) {
                    <lib-badge variant="default" class="board-selector_default-badge"
                      >Default</lib-badge
                    >
                  }
                </div>
                <div class="board-selector_item-actions">
                  @if (!board.is_default) {
                    <lib-button
                      variant="ghost"
                      size="sm"
                      [iconOnly]="true"
                      leftIcon="star"
                      (clicked)="handleSetDefaultBoard(board.id, $event)"
                    />
                  }
                  <lib-button
                    variant="ghost"
                    size="sm"
                    [iconOnly]="true"
                    leftIcon="copy"
                    (clicked)="handleDuplicateBoard(board.id, $event)"
                  />
                  <lib-button
                    variant="ghost"
                    size="sm"
                    [iconOnly]="true"
                    leftIcon="trash"
                    (clicked)="handleDeleteBoard(board.id, $event)"
                  />
                </div>
              </button>
            }
          }
        </div>
      </div>
    </ng-template>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .board-selector_button {
        @apply min-w-52;
      }

      .board-selector_button-content {
        @apply flex items-center justify-between;
        @apply w-full gap-2;
      }

      .board-selector_current-name {
        @apply truncate;
      }

      .board-selector_chevron {
        @apply text-muted-foreground;
      }

      .board-selector_dropdown {
        @apply w-80;
        @apply p-2;
        @apply flex flex-col gap-2;
      }

      .board-selector_create {
        @apply justify-start;
      }

      .board-selector_list {
        @apply flex flex-col;
        @apply max-h-64 overflow-y-auto;
      }

      .board-selector_item {
        @apply w-full text-left;
        @apply px-3 py-2;
        @apply rounded-md;
        @apply flex items-center justify-between gap-2;
        @apply hover:bg-accent;
      }

      .board-selector_item-main {
        @apply flex items-center gap-2 min-w-0;
      }

      .board-selector_item-actions {
        @apply flex items-center gap-1;
      }

      .board-selector_item--active {
        @apply bg-accent;
      }

      .board-selector_item-name {
        @apply text-sm truncate;
      }

      .board-selector_default-badge {
        @apply text-xs;
      }

      .board-selector_type-badge {
        @apply shrink-0 text-xs;
      }

      .board-selector_empty {
        @apply px-3 py-4 text-sm text-muted-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BoardSelector {
  readonly boards = input<BoardResponse[]>([]);
  readonly selectedBoardId = input<string | null>(null);
  readonly boardSelected = output<string>();
  readonly createBoard = output<void>();
  readonly createGroupBoard = output<void>();
  readonly duplicateBoard = output<string>();
  readonly deleteBoard = output<string>();
  readonly setDefaultBoard = output<string>();

  readonly searchQuery = model('');

  readonly selectedBoardName = computed(() => {
    const selectedId = this.selectedBoardId();
    const selectedBoard = this.boards().find((board) => board.id === selectedId);
    return selectedBoard?.name ?? 'Select board';
  });

  readonly filteredBoards = computed(() => {
    const query = this.searchQuery().trim().toLowerCase();
    if (!query) {
      return this.boards();
    }
    return this.boards().filter((board) => board.name.toLowerCase().includes(query));
  });

  handleSelectBoard(boardId: string, dropdown: Dropdown): void {
    this.boardSelected.emit(boardId);
    dropdown.open.set(false);
  }

  handleCreateBoard(dropdown: Dropdown): void {
    this.createBoard.emit();
    dropdown.open.set(false);
  }

  handleCreateGroupBoard(dropdown: Dropdown): void {
    this.createGroupBoard.emit();
    dropdown.open.set(false);
  }

  handleDuplicateBoard(boardId: string, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.duplicateBoard.emit(boardId);
  }

  handleDeleteBoard(boardId: string, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.deleteBoard.emit(boardId);
  }

  handleSetDefaultBoard(boardId: string, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.setDefaultBoard.emit(boardId);
  }
}
