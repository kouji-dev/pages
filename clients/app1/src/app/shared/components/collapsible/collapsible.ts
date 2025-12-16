import { Component, ChangeDetectionStrategy, signal, input, output, effect, ContentChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-collapsible',
  imports: [CommonModule],
  template: `
    <div class="collapsible">
      <ng-content />
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .collapsible {
        @apply w-full;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class Collapsible implements AfterViewInit {
  open = input(false);
  readonly isOpen = signal(this.open());

  readonly onOpenChange = output<boolean>();

  private triggerElement: HTMLElement | null = null;
  private contentElement: HTMLElement | null = null;

  private readonly openEffect = effect(() => {
    const openValue = this.open();
    if (openValue !== this.isOpen()) {
      this.isOpen.set(openValue);
    }
  });

  ngAfterViewInit(): void {
    // Find trigger and content elements
    if (typeof document !== 'undefined') {
      const host = document.querySelector('app-collapsible');
      if (host) {
        this.triggerElement = host.querySelector('[trigger]') as HTMLElement;
        this.contentElement = host.querySelector('[content]') as HTMLElement;

        // Add click handler to trigger
        if (this.triggerElement) {
          this.triggerElement.addEventListener('click', () => this.toggle());
        }
      }
    }
  }

  toggle(): void {
    this.isOpen.update((current) => !current);
    this.onOpenChange.emit(this.isOpen());
    this.updateContentVisibility();
  }

  setOpen(open: boolean): void {
    this.isOpen.set(open);
    this.onOpenChange.emit(open);
    this.updateContentVisibility();
  }

  private updateContentVisibility(): void {
    if (this.contentElement) {
      if (this.isOpen()) {
        this.contentElement.style.display = 'block';
      } else {
        this.contentElement.style.display = 'none';
      }
    }
  }
}
