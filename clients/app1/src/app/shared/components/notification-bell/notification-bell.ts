import {
  Component,
  ChangeDetectionStrategy,
  signal,
  inject,
  computed,
  ViewChild,
  ElementRef,
  TemplateRef,
  ViewContainerRef,
  OnDestroy,
} from '@angular/core';
import { Overlay, OverlayRef, OverlayConfig } from '@angular/cdk/overlay';
import { TemplatePortal } from '@angular/cdk/portal';
import { Icon } from 'shared-ui';
import { NotificationService } from '../../../application/services/notification.service';
import { NotificationDropdown } from '../notification-dropdown/notification-dropdown';

@Component({
  selector: 'app-notification-bell',
  imports: [Icon, NotificationDropdown],
  template: `
    <div class="notification-bell" #bellContainer>
      <button
        type="button"
        class="notification-bell_button"
        (click)="toggleDropdown()"
        [attr.aria-label]="'Notifications'"
        [attr.aria-expanded]="isDropdownOpen()"
      >
        <lib-icon name="bell" size="md" class="notification-bell_icon" />
        @if (unreadCount() > 0) {
          <span class="notification-bell_badge">{{ displayCount() }}</span>
        }
      </button>
    </div>

    <!-- Dropdown Template -->
    <ng-template #dropdownTemplate>
      <app-notification-dropdown (close)="closeDropdown()" />
    </ng-template>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .notification-bell {
        @apply relative;
      }

      .notification-bell_button {
        @apply relative;
        @apply p-2;
        @apply rounded-md;
        @apply border-none;
        @apply bg-transparent;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-accent;
        @apply active:bg-accent;
        @apply flex items-center justify-center;
        @apply text-muted-foreground;
        @apply hover:text-foreground;
      }

      .notification-bell_icon {
        @apply relative;
      }

      .notification-bell_badge {
        @apply absolute;
        @apply top-0;
        @apply right-0;
        @apply min-w-[18px];
        @apply h-[18px];
        @apply px-1;
        @apply flex items-center justify-center;
        @apply text-xs;
        @apply font-semibold;
        @apply text-white;
        @apply bg-destructive;
        @apply rounded-full;
        @apply border-2;
        @apply border-background;
        transform: translate(25%, -25%);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NotificationBell implements OnDestroy {
  private readonly notificationService = inject(NotificationService);
  private readonly overlay = inject(Overlay);
  private readonly viewContainerRef = inject(ViewContainerRef);

  @ViewChild('bellContainer', { static: false }) bellContainer?: ElementRef<HTMLDivElement>;
  @ViewChild('dropdownTemplate', { static: false }) dropdownTemplate?: TemplateRef<any>;

  readonly isDropdownOpen = signal<boolean>(false);
  private overlayRef: OverlayRef | null = null;

  readonly unreadCount = this.notificationService.unreadCountValue;

  readonly displayCount = computed(() => {
    const count = this.unreadCount();
    return count > 99 ? '99+' : count.toString();
  });

  ngOnDestroy(): void {
    this.closeDropdown();
  }

  toggleDropdown(): void {
    if (this.isDropdownOpen()) {
      this.closeDropdown();
    } else {
      this.openDropdown();
    }
  }

  private openDropdown(): void {
    if (this.isDropdownOpen() || !this.dropdownTemplate || !this.bellContainer) {
      return;
    }

    // Load notifications when opening dropdown
    this.notificationService.setFilters({ page: 1, limit: 20, read: null });

    const config: OverlayConfig = {
      positionStrategy: this.overlay
        .position()
        .flexibleConnectedTo(this.bellContainer.nativeElement)
        .withPositions([
          {
            originX: 'end',
            originY: 'bottom',
            overlayX: 'end',
            overlayY: 'top',
            offsetY: 8,
          },
        ])
        .withFlexibleDimensions(true)
        .withPush(true),
      scrollStrategy: this.overlay.scrollStrategies.reposition(),
      panelClass: 'notification-dropdown-overlay',
      backdropClass: 'cdk-overlay-transparent-backdrop',
      hasBackdrop: true,
      disposeOnNavigation: true,
    };

    this.overlayRef = this.overlay.create(config);
    const portal = new TemplatePortal(this.dropdownTemplate, this.viewContainerRef);
    this.overlayRef.attach(portal);
    this.isDropdownOpen.set(true);

    // Handle backdrop clicks
    this.overlayRef.backdropClick().subscribe(() => {
      this.closeDropdown();
    });

    // Handle escape key
    this.overlayRef.keydownEvents().subscribe((event) => {
      if (event.key === 'Escape') {
        this.closeDropdown();
      }
    });
  }

  closeDropdown(): void {
    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
    }
    this.isDropdownOpen.set(false);
  }
}
