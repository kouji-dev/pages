import {
  Component,
  ChangeDetectionStrategy,
  input,
  effect,
  signal,
  HostListener,
} from '@angular/core';
import { CommonModule } from '@angular/common';

export interface SidenavItem {
  label: string;
  anchor: string;
}

@Component({
  selector: 'lib-sidenav',
  imports: [CommonModule],
  template: `
    <nav class="sidenav">
      <div class="sidenav_header">
        <h3 class="sidenav_title">{{ title() }}</h3>
      </div>
      <ul class="sidenav_list">
        @for (item of items(); track item.anchor) {
          <li class="sidenav_item">
            <a
              class="sidenav_link"
              [class.sidenav_link--active]="activeAnchor() === item.anchor"
              [href]="'#' + item.anchor"
              (click)="scrollToAnchor($event, item.anchor)"
            >
              <span class="sidenav_link-text">{{ item.label }}</span>
            </a>
          </li>
        }
      </ul>
    </nav>
  `,
  styles: [
    `
      @reference "#theme";

      .sidenav {
        @apply fixed;
        @apply right-4;
        @apply top-4;
        @apply w-64;
        @apply max-h-[calc(100vh-2rem)];
        @apply bg-card;
        @apply border border-border;
        @apply rounded-lg;
        @apply overflow-y-auto;
        @apply flex flex-col;
        @apply z-40;
      }

      .sidenav_header {
        @apply flex items-center;
        @apply p-4;
        @apply border-b border-border;
      }

      .sidenav_title {
        @apply text-lg font-semibold;
        @apply text-foreground;
        @apply whitespace-nowrap;
      }

      .sidenav_list {
        @apply flex flex-col;
        @apply p-2;
        @apply list-none;
        @apply m-0;
      }

      .sidenav_item {
        @apply mb-1;
      }

      .sidenav_link {
        @apply flex items-center;
        @apply px-3 py-2;
        @apply rounded;
        @apply text-sm;
        @apply text-muted-foreground;
        @apply hover:text-foreground;
        @apply hover:bg-muted;
        @apply transition-colors;
        @apply no-underline;
        @apply cursor-pointer;
      }

      .sidenav_link--active {
        @apply text-primary;
        @apply bg-primary/10;
        @apply font-medium;
      }

      .sidenav_link-text {
        @apply whitespace-nowrap;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Sidenav {
  readonly title = input<string>('Navigation');
  readonly items = input.required<SidenavItem[]>();

  readonly activeAnchor = signal<string>('');

  @HostListener('window:scroll', [])
  onScroll(): void {
    this.updateActiveAnchor();
  }

  @HostListener('window:resize', [])
  onResize(): void {
    this.updateActiveAnchor();
  }

  private readonly updateActiveAnchorEffect = effect(() => {
    // Trigger update when items change
    this.items();
    // Use setTimeout to ensure DOM is ready
    setTimeout(() => this.updateActiveAnchor(), 0);
  });

  scrollToAnchor(event: Event, anchor: string): void {
    event.preventDefault();
    const element = document.getElementById(anchor);
    if (element) {
      const headerOffset = 80; // Adjust based on your header height
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      });

      // Update active anchor immediately
      this.activeAnchor.set(anchor);
    }
  }

  private updateActiveAnchor(): void {
    const items = this.items();
    if (items.length === 0) return;

    const scrollPosition = window.scrollY + 100; // Offset for header

    // Find the section that's currently in view
    let activeAnchor = items[0].anchor;

    for (const item of items) {
      const element = document.getElementById(item.anchor);
      if (element) {
        const elementTop = element.offsetTop;
        if (scrollPosition >= elementTop) {
          activeAnchor = item.anchor;
        } else {
          break;
        }
      }
    }

    this.activeAnchor.set(activeAnchor);
  }
}
