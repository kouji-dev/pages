import {
  Component,
  ChangeDetectionStrategy,
  computed,
  signal,
  effect,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { Button } from '../../button/button';
import { Input } from '../../input/input';
import { BaseNodeComponent } from './base-node-component';
import { ImageNode } from '../nodes/image-node';

@Component({
  selector: 'lib-text-editor-image-decorator',
  imports: [Button, Input],
  template: `
    <div class="te-image-decorator" [attr.data-image-src]="src()">
      <div class="te-image-decorator_wrapper" [style.width.px]="width() || 'auto'">
        <img
          #imageElement
          [src]="src()"
          [alt]="alt()"
          [style.width.px]="width() || 'auto'"
          [style.height.px]="height() || 'auto'"
          class="te-image-decorator_image"
          draggable="false"
        />
        <div class="te-image-decorator_overlay">
          <div class="te-image-decorator_actions">
            <lib-button variant="ghost" size="sm" (clicked)="editAlt()" leftIcon="pen" />
          </div>
        </div>
      </div>
      @if (showAltEditor()) {
        <div
          class="te-image-decorator_alt-editor"
          (keydown.enter)="saveAlt()"
          (keydown.escape)="cancelAltEdit()"
        >
          <lib-input
            type="text"
            [model]="altText()"
            (modelChange)="altText.set($event)"
            (blurred)="saveAlt()"
            placeholder="Alt text"
          />
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .te-image-decorator {
        @apply inline-block;
        @apply my-2;
        @apply relative;
      }

      .te-image-decorator_wrapper {
        @apply relative;
        @apply inline-block;
        @apply rounded-lg;
        @apply overflow-hidden;
        @apply border;
        @apply border-border-default;
      }

      .te-image-decorator_image {
        @apply block;
        @apply max-w-full;
        @apply h-auto;
        @apply object-contain;
      }

      .te-image-decorator_overlay {
        @apply absolute;
        @apply inset-0;
        @apply bg-bg-overlay;
        @apply opacity-0;
        @apply hover:opacity-100;
        @apply transition-opacity;
        @apply flex items-center justify-center;
      }

      .te-image-decorator_actions {
        @apply flex items-center gap-2;
      }

      .te-image-decorator_alt-editor {
        @apply mt-2;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ImageDecoratorComponent extends BaseNodeComponent<ImageNode> {
  readonly src = computed(() => {
    const node = this.currentNode();
    return node ? node.getSrc() : '';
  });

  readonly alt = computed(() => {
    const node = this.currentNode();
    return node ? node.getAlt() : '';
  });

  readonly width = computed(() => {
    const node = this.currentNode();
    return node ? node.getWidth() : 0;
  });

  readonly height = computed(() => {
    const node = this.currentNode();
    return node ? node.getHeight() : 0;
  });

  @ViewChild('imageElement') imageElement?: ElementRef<HTMLImageElement>;

  readonly showAltEditor = signal(false);
  readonly altText = signal('');

  private readonly altEffect = effect(() => {
    this.altText.set(this.alt());
  });

  editAlt(): void {
    this.showAltEditor.set(true);
  }

  saveAlt(): void {
    // TODO: Update the image node's alt text via editor
    this.showAltEditor.set(false);
  }

  cancelAltEdit(): void {
    this.altText.set(this.alt());
    this.showAltEditor.set(false);
  }
}
