import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  effect,
  DestroyRef,
  inject,
  signal,
  computed,
  linkedSignal,
  forwardRef,
  ElementRef,
  ViewChild,
  AfterViewInit,
  ViewContainerRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { $getRoot, LexicalEditor, SerializedEditorState, SerializedLexicalNode } from 'lexical';
import { $generateHtmlFromNodes, $generateNodesFromDOM } from '@lexical/html';
import { TEXT_EDITOR_PLUGINS } from './text-editor.tokens';
import { HistoryPlugin } from './plugins/history-plugin';
import { ListPlugin } from './plugins/list-plugin';
import { LinkPlugin } from './plugins/link-plugin';
import { RichTextPlugin } from './plugins/rich-text-plugin';
import { HeadingPlugin } from './plugins/heading-plugin';
import { FontSizePlugin } from './plugins/font-size-plugin';
import { AttachmentPlugin } from './plugins/attachment-plugin';
import { ImagePlugin } from './plugins/image-plugin';
import { DecoratorsPlugin } from './plugins/decorators-plugin';
import { TextEditorToolbar } from './text-editor-toolbar';
import { TextEditorService } from './text-editor.service';
import { MentionPlugin } from './plugins/mention-plugin';
import { TypeaheadMenuPlugin } from './plugins/typeahead-menu-plugin';
import { SharedUiTranslateService } from '../i18n/shared-ui-translate.service';

@Component({
  selector: 'lib-text-editor',
  imports: [CommonModule, TextEditorToolbar],
  providers: [
    TextEditorService,
    HistoryPlugin,
    ListPlugin,
    LinkPlugin,
    RichTextPlugin,
    HeadingPlugin,
    FontSizePlugin,
    AttachmentPlugin,
    ImagePlugin,
    DecoratorsPlugin,
    MentionPlugin,
    TypeaheadMenuPlugin,
    { provide: TEXT_EDITOR_PLUGINS, useExisting: HistoryPlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: ListPlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: LinkPlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: RichTextPlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: HeadingPlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: FontSizePlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: AttachmentPlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: ImagePlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: DecoratorsPlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: MentionPlugin, multi: true },
    { provide: TEXT_EDITOR_PLUGINS, useExisting: TypeaheadMenuPlugin, multi: true },
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => TextEditor),
      multi: true,
    },
  ],
  template: `
    <div class="text-editor">
      <lib-text-editor-toolbar [showToolbar]="showToolbar()" />
      <div class="text-editor_wrapper">
        <div
          #editorContainer
          class="text-editor_container text-editor_content"
          [attr.data-placeholder]="placeholder()"
          [contentEditable]="editable()"
          [class.text-editor_container--disabled]="isDisabled()"
          [class.text-editor_container--error]="errorMessage()"
          spellcheck="true"
          role="textbox"
          [attr.aria-multiline]="true"
          (blur)="onTouched()"
        ></div>
      </div>
      @if (errorMessage()) {
        <div class="text-editor_error">{{ errorMessage() }}</div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .text-editor {
        @apply flex flex-col;
        @apply border border-border-default rounded-lg;
        @apply bg-bg-primary;
      }

      .text-editor_toolbar {
        @apply flex items-center gap-1;
        @apply p-2;
        @apply border-b border-border-default;
        @apply bg-bg-secondary;
        @apply flex-wrap;
      }

      .text-editor_toolbar-group {
        @apply flex items-center gap-1;
      }

      .text-editor_toolbar-separator {
        @apply w-px h-6;
        @apply bg-border-default;
        @apply mx-1;
      }

      .text-editor_toolbar-button {
        @apply px-2 py-1;
        @apply rounded;
        @apply text-sm;
        @apply text-text-primary;
        @apply bg-transparent;
        @apply border border-transparent;
        @apply hover:bg-bg-tertiary;
        @apply active:bg-bg-tertiary;
        @apply transition-colors;
        @apply cursor-pointer;
        @apply min-w-[32px];
        @apply flex items-center justify-center;
      }

      .text-editor_toolbar-button.active {
        @apply bg-primary-100;
        @apply border-primary-300;
        @apply text-primary-700;
      }

      .text-editor_toolbar-button:disabled {
        @apply opacity-50;
        @apply cursor-not-allowed;
      }

      .text-editor_wrapper {
        @apply flex-1;
        @apply min-h-0;
      }

      .text-editor_container {
        @apply min-h-[120px];
        @apply p-3;
        @apply focus-within:outline-none;
      }

      .text-editor_container--disabled {
        @apply opacity-50;
        @apply cursor-not-allowed select-none;
      }

      .text-editor_container--error {
        @apply border-error;
      }

      .text-editor_error {
        @apply text-xs text-error;
        @apply mt-1 px-3;
      }

      :host ::ng-deep .text-editor_content {
        @apply min-h-[100px];
        @apply outline-none;
        @apply text-text-primary;
        @apply leading-relaxed;
        @apply overflow-auto;
      }

      :host ::ng-deep .text-editor_content[data-placeholder]:empty::before {
        content: attr(data-placeholder);
        @apply text-text-tertiary;
        @apply pointer-events-none;
      }

      /* Lexical theme classes - simplified with te- prefix */
      :host ::ng-deep .te-paragraph {
        @apply mb-2;
      }

      :host ::ng-deep .te-h1 {
        @apply text-4xl font-bold mb-4;
        @apply text-text-primary;
      }

      :host ::ng-deep .te-h2 {
        @apply text-3xl font-semibold mb-3;
        @apply text-text-primary;
      }

      :host ::ng-deep .te-h3 {
        @apply text-2xl font-semibold mb-2;
        @apply text-text-primary;
      }

      :host ::ng-deep .te-ul {
        @apply list-disc mb-2;
        @apply ml-6;
        @apply pl-0;
      }

      :host ::ng-deep .te-ol {
        @apply list-decimal mb-2;
        @apply ml-6;
        @apply pl-0;
      }

      :host ::ng-deep .te-li {
        @apply mb-1;
      }

      :host ::ng-deep .te-link {
        @apply text-text-link;
        @apply underline;
      }

      :host ::ng-deep .te-bold {
        @apply font-bold;
      }

      :host ::ng-deep .te-italic {
        @apply italic;
      }

      :host ::ng-deep .te-underline {
        @apply underline;
      }

      :host ::ng-deep .te-strikethrough {
        @apply line-through;
      }

      :host ::ng-deep .te-code {
        @apply bg-bg-tertiary;
        @apply px-1 py-0.5;
        @apply rounded;
        @apply font-mono;
        @apply text-sm;
      }

      :host ::ng-deep .te-quote {
        @apply border-l-4 border-border-default;
        @apply pl-4;
        @apply italic;
        @apply text-text-secondary;
        @apply my-2;
      }

      /* Font size inline styles - these are applied via the plugin */
      :host ::ng-deep [style*='font-size: var(--text-xs)'] {
        font-size: var(--text-xs) !important;
      }

      :host ::ng-deep [style*='font-size: var(--text-sm)'] {
        font-size: var(--text-sm) !important;
      }

      :host ::ng-deep [style*='font-size: var(--text-md)'] {
        font-size: var(--text-base) !important;
      }

      :host ::ng-deep [style*='font-size: var(--text-lg)'] {
        font-size: var(--text-lg) !important;
      }

      :host ::ng-deep [style*='font-size: var(--text-xl)'] {
        font-size: var(--text-xl) !important;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TextEditor implements ControlValueAccessor, AfterViewInit {
  private readonly editorService = inject(TextEditorService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly plugins = inject(TEXT_EDITOR_PLUGINS, { optional: true }) || [];
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(SharedUiTranslateService);

  @ViewChild('editorContainer', { static: false }) editorContainer!: ElementRef<HTMLDivElement>;

  readonly placeholderInput = input<string>('');

  readonly placeholder = computed(() => {
    const customPlaceholder = this.placeholderInput();
    return customPlaceholder || this.translateService.instant('textEditor.placeholder');
  });
  readonly disabled = input<boolean>(false);
  readonly readOnly = input<boolean>(false);
  readonly errorMessage = input<string | undefined>(undefined);
  readonly showToolbar = input<boolean>(true);
  readonly initialValue = input<string | undefined>(undefined);

  readonly valueChange = output<string>();
  readonly htmlChange = output<string>();
  readonly jsonChange = output<SerializedEditorState<SerializedLexicalNode>>();
  readonly disabledChange = output<boolean>();

  // ControlValueAccessor implementation
  private onChange = (value: string) => {};
  onTouched = () => {};

  // Linked signal for disabled state - linked only to disabled input
  readonly isDisabled = linkedSignal(() => this.disabled());

  // Computed editable state
  readonly editable = computed(() => !this.isDisabled() && !this.readOnly());

  private initialized = false;

  // Handle editable state changes
  private readonly editableEffect = effect(() => {
    const editor = this.editorService.editor;
    if (!editor) return;

    editor.setEditable(this.editable());
  });

  // Emit disabled state changes
  private readonly disabledChangeEffect = effect(() => {
    this.disabledChange.emit(this.isDisabled());
  });

  constructor() {
    // Register cleanup
    this.destroyRef.onDestroy(() => {
      this.cleanup();
    });
  }

  ngAfterViewInit(): void {
    if (this.editorContainer?.nativeElement) {
      this.setupEditor(this.editorContainer.nativeElement);
    }
  }

  private setupEditor(container: HTMLDivElement): void {
    if (this.initialized) return;

    // Create editor via service (plugins are registered automatically)
    this.editorService.createEditor(
      this.plugins,
      this.initialValue(),
      (html, text) => {
        const editor = this.editorService.editor;
        const json = editor ? editor.getEditorState().toJSON() : null;
        this.htmlChange.emit(html);
        this.valueChange.emit(text);
        if (json) {
          this.jsonChange.emit(json);
        }
        // Notify form control of value change
        this.onChange(html);
      },
      this.viewContainerRef,
    );

    this.editorService.setRootElement(container);

    this.initialized = true;
  }

  getEditor(): LexicalEditor | null {
    return this.editorService.editor;
  }

  getHtml(): string {
    const editor = this.editorService.editor;
    if (!editor) return '';
    let html = '';
    editor.getEditorState().read(() => {
      html = $generateHtmlFromNodes(editor, null);
    });
    return html;
  }

  setHtml(html: string): void {
    const editor = this.editorService.editor;
    if (!editor) return;
    editor.update(() => {
      const root = $getRoot();
      root.clear();
      const parser = new DOMParser();
      const dom = parser.parseFromString(html, 'text/html');
      const nodes = $generateNodesFromDOM(editor, dom);
      root.append(...nodes);
    });
  }

  getJson(): SerializedEditorState<SerializedLexicalNode> | null {
    return this.editorService.getJSON();
  }

  setJson(json: SerializedEditorState<SerializedLexicalNode>): void {
    this.editorService.setJSON(json);
  }

  // ControlValueAccessor implementation
  writeValue(value: string | null): void {
    if (value === null || value === undefined) {
      value = '';
    }
    // Only update if value is different to avoid infinite loops
    const currentHtml = this.getHtml();
    if (currentHtml !== value) {
      this.setHtml(value);
    }
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.isDisabled.set(isDisabled);
  }

  private cleanup(): void {
    // Clean up editor via service (plugins are unregistered automatically)
    this.editorService.destroy();
    this.initialized = false;
  }
}
