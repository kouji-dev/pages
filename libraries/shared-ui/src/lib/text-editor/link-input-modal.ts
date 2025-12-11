import {
  Component,
  ChangeDetectionStrategy,
  inject,
  ViewChild,
  ElementRef,
  afterNextRender,
  input,
  signal,
  effect,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Modal } from '../modal/modal';
import { ModalContainer } from '../modal/modal-container';
import { ModalHeader } from '../modal/modal-header';
import { ModalContent } from '../modal/modal-content';
import { ModalFooter } from '../modal/modal-footer';
import { Button } from '../button/button';
import { Input } from '../input/input';

@Component({
  selector: 'lib-link-input-modal',
  imports: [CommonModule, ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input],
  template: `
    <lib-modal-container>
      <lib-modal-header>
        <h2>Add Link</h2>
      </lib-modal-header>
      <lib-modal-content>
        <lib-input
          #urlInput
          type="text"
          label="URL"
          placeholder="https://example.com"
          [model]="url()"
          (modelChange)="url.set($event)"
          (keydown.enter)="onSubmit()"
        />
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="ghost" (clicked)="onCancel()">Cancel</lib-button>
        <lib-button variant="primary" (clicked)="onSubmit()">Add Link</lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LinkInputModal {
  private readonly modal = inject(Modal);
  @ViewChild('urlInput', { static: false }) urlInput?: ElementRef<HTMLElement>;

  readonly initialUrl = input<string>('');
  readonly url = signal(this.initialUrl());

  constructor() {
    // Update url signal when initialUrl changes
    effect(() => {
      const initial = this.initialUrl();
      if (initial) {
        this.url.set(initial);
      }
    });

    afterNextRender(() => {
      // Focus the input after render
      if (this.urlInput?.nativeElement) {
        const input = this.urlInput.nativeElement.querySelector('input');
        if (input) {
          input.focus();
        }
      }
    });
  }

  onSubmit(): void {
    this.modal.close(this.url());
  }

  onCancel(): void {
    this.modal.close(null);
  }
}
