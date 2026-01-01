import { Component, computed, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon, Avatar, IconName, Badge } from 'shared-ui';
import { IssueListItem } from '../../../application/services/issue.service';
import { SeverityBadge } from '../severity-badge';

@Component({
  selector: 'app-issue-card',
  standalone: true,
  imports: [CommonModule, Icon, Avatar, SeverityBadge, Badge],
  template: `
    <div class="issue-card" (click)="handleClick()">
      <p class="issue-card_title">{{ issue().title }}</p>

      <div class="issue-card_footer">
        <div class="issue-card_footer-left">
          <lib-icon [name]="typeIcon()" [size]="'xs'" [class]="typeIconClass()" />
          <span class="issue-card_key">{{ issue().key }}</span>
          <app-severity-badge [severity]="issue().priority" />
        </div>
        <div class="issue-card_footer-right">
          @if (issue().priority === 'high' || issue().priority === 'critical') {
            <lib-icon name="arrow-up" [size]="'xs'" class="issue-card_priority-icon" />
          }
          @if (showStoryPoints() && issue().story_points) {
            <lib-badge variant="default" class="issue-card_story-points">
              {{ issue().story_points }}
            </lib-badge>
          }
          @if (issue().assignee_id && assignee(); as assigneeData) {
            <lib-avatar
              [avatarUrl]="assigneeData.avatar_url || undefined"
              [name]="assigneeData.user_name"
              [initials]="getInitials(assigneeData.user_name)"
              size="sm"
            />
          }
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-card {
        @apply p-4;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-card;
        @apply cursor-pointer;
        @apply hover:bg-accent/50;
        @apply transition-colors;
      }

      .issue-card.cdk-drag-animating {
        @apply transition-transform;
      }

      .issue-card_title {
        @apply text-sm font-medium;
        @apply text-foreground;
        @apply mb-3;
        margin: 0 0 0.75rem 0;
      }

      .issue-card_footer {
        @apply flex items-center justify-between;
        @apply gap-2;
      }

      .issue-card_footer-left {
        @apply flex items-center;
        @apply gap-2;
      }

      .issue-card_footer-right {
        @apply flex items-center;
        @apply gap-2;
      }

      .issue-card_key {
        @apply text-xs;
        @apply text-muted-foreground;
        @apply font-mono;
      }

      .issue-card_priority-icon {
        @apply text-red-500;
      }

      .issue-card_type-icon--task {
        @apply text-blue-500;
      }

      .issue-card_type-icon--bug {
        @apply text-red-500;
      }

      .issue-card_type-icon--story {
        @apply text-green-500;
      }

      .issue-card_type-icon--epic {
        @apply text-purple-500;
      }

      .issue-card_story-points {
        @apply text-xs;
        @apply h-5;
        @apply min-w-5;
        @apply flex items-center justify-center;
        @apply rounded-full;
      }
    `,
  ],
})
export class IssueCard {
  issue = input.required<IssueListItem>();
  assignee = input<{ user_name: string; avatar_url?: string } | null>(null);
  showStoryPoints = input<boolean>(false);

  readonly onClick = output<IssueListItem>();

  readonly typeIcon = computed<IconName>(() => {
    switch (this.issue().type) {
      case 'task':
        return 'square-check';
      case 'bug':
        return 'bug';
      case 'story':
        return 'book-open';
      case 'epic':
        return 'folder';
      default:
        return 'circle';
    }
  });

  readonly typeIconClass = computed(() => {
    return `issue-card_type-icon--${this.issue().type}`;
  });

  handleClick(): void {
    this.onClick.emit(this.issue());
  }

  getInitials(name: string): string {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }
}
