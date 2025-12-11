import {
  Injectable,
  inject,
  ViewContainerRef,
  ComponentRef,
  signal,
  DestroyRef,
  Signal,
  effect,
  Injector,
} from '@angular/core';
import {
  LexicalEditor,
  $getSelection,
  $isRangeSelection,
  $isTextNode,
  TextNode,
  RangeSelection,
  getDOMSelection,
  COMMAND_PRIORITY_LOW,
  CommandListenerPriority,
  KEY_ARROW_DOWN_COMMAND,
  KEY_ARROW_UP_COMMAND,
  KEY_ENTER_COMMAND,
  KEY_ESCAPE_COMMAND,
  KEY_TAB_COMMAND,
  createCommand,
  LexicalCommand,
} from 'lexical';
import {
  Overlay,
  OverlayRef,
  OverlayConfig,
  FlexibleConnectedPositionStrategy,
} from '@angular/cdk/overlay';
import { ComponentPortal } from '@angular/cdk/portal';
import { TextEditorPlugin } from './plugin';
import { MentionAutocompleteComponent } from '../mention/mention-autocomplete.component';
import type { MentionOption } from '../interfaces/mention-list-provider.interface';

export const PUNCTUATION = '\\.,\\+\\*\\?\\$\\@\\|#{}\\(\\)\\^\\-\\[\\]\\\\/!%\'"~=<>_:;';

export interface MenuTextMatch {
  leadOffset: number;
  matchingString: string;
  replaceableString: string;
}

export interface MenuResolution {
  getRect: () => DOMRect;
  match: MenuTextMatch;
}

export type TriggerFn = (text: string, editor: LexicalEditor) => MenuTextMatch | null;

export interface MenuOption {
  key: string;
  [key: string]: any;
}

export interface TypeaheadMenuPluginConfig<TOption extends MenuOption> {
  onQueryChange: (matchingString: string | null) => void;
  onSelectOption: (
    option: TOption,
    textNodeContainingQuery: TextNode | null,
    closeMenu: () => void,
    matchingString: string,
  ) => void;
  options: Signal<TOption[]>; // Signal for current options
  triggerFn: TriggerFn;
  menuComponent?: any; // Component type for rendering menu
  onOpen?: (resolution: MenuResolution) => void;
  onClose?: () => void;
  commandPriority?: CommandListenerPriority;
  parent?: HTMLElement;
  preselectFirstItem?: boolean;
  ignoreEntityBoundary?: boolean;
}

/**
 * Get text up to the anchor point in the selection
 */
function getTextUpToAnchor(selection: RangeSelection): string | null {
  const anchor = selection.anchor;
  if (anchor.type !== 'text') {
    return null;
  }
  const anchorNode = anchor.getNode();
  if (!$isTextNode(anchorNode) || !anchorNode.isSimpleText()) {
    return null;
  }
  const anchorOffset = anchor.offset;
  return anchorNode.getTextContent().slice(0, anchorOffset);
}

/**
 * Try to position a range at the cursor location
 */
function tryToPositionRange(leadOffset: number, range: Range, editorWindow: Window): boolean {
  const domSelection = getDOMSelection(editorWindow);
  if (domSelection === null || !domSelection.isCollapsed) {
    return false;
  }
  const anchorNode = domSelection.anchorNode;
  const startOffset = leadOffset;
  const endOffset = domSelection.anchorOffset;

  if (anchorNode == null || endOffset == null) {
    return false;
  }

  try {
    range.setStart(anchorNode, startOffset);
    range.setEnd(anchorNode, endOffset);
  } catch (_error) {
    return false;
  }

  return true;
}

/**
 * Get query text for search
 */
function getQueryTextForSearch(editor: LexicalEditor): string | null {
  let text = null;
  editor.getEditorState().read(() => {
    const selection = $getSelection();
    if (!$isRangeSelection(selection)) {
      return;
    }
    text = getTextUpToAnchor(selection);
  });
  return text;
}

/**
 * Check if selection is on entity boundary
 */
function isSelectionOnEntityBoundary(editor: LexicalEditor, offset: number): boolean {
  if (offset !== 0) {
    return false;
  }
  return editor.getEditorState().read(() => {
    const selection = $getSelection();
    if ($isRangeSelection(selection)) {
      const anchor = selection.anchor;
      const anchorNode = anchor.getNode();
      const prevSibling = anchorNode.getPreviousSibling();
      return $isTextNode(prevSibling) && prevSibling.isTextEntity();
    }
    return false;
  });
}

/**
 * Basic typeahead trigger match function
 */
export function createBasicTypeaheadTriggerMatch(
  trigger: string,
  options: {
    minLength?: number;
    maxLength?: number;
    punctuation?: string;
    allowWhitespace?: boolean;
  } = {},
): TriggerFn {
  const {
    minLength = 1,
    maxLength = 75,
    punctuation = PUNCTUATION,
    allowWhitespace = false,
  } = options;

  return (text: string) => {
    const validCharsSuffix = allowWhitespace ? '' : '\\s';
    const validChars = '[^' + trigger + punctuation + validCharsSuffix + ']';
    const TypeaheadTriggerRegex = new RegExp(
      '(^|\\s|\\()(' + '[' + trigger + ']' + '((?:' + validChars + '){0,' + maxLength + '})' + ')$',
    );
    const match = TypeaheadTriggerRegex.exec(text);
    if (match !== null) {
      const maybeLeadingWhitespace = match[1];
      const matchingString = match[3];
      if (matchingString.length >= minLength) {
        return {
          leadOffset: match.index + maybeLeadingWhitespace.length,
          matchingString,
          replaceableString: match[2],
        };
      }
    }
    return null;
  };
}

/**
 * Typeahead Menu Plugin - Angular adaptation of LexicalTypeaheadMenuPlugin
 */
@Injectable()
export class TypeaheadMenuPlugin<TOption extends MenuOption> implements TextEditorPlugin {
  private readonly overlay = inject(Overlay);
  private readonly destroyRef = inject(DestroyRef);
  private readonly injector = inject(Injector);
  private editor: LexicalEditor | null = null;
  private viewContainerRef: ViewContainerRef | null = null;
  private config: TypeaheadMenuPluginConfig<TOption> | null = null;
  private overlayRef: OverlayRef | null = null;
  private menuComponentRef: ComponentRef<any> | null = null;
  private resolution: MenuResolution | null = null;
  private unregisterListeners: (() => void)[] = [];
  private optionsEffectCleanup: (() => void) | null = null;

  register(
    editor: LexicalEditor,
    rootElement?: HTMLElement,
    viewContainerRef?: ViewContainerRef,
  ): () => void {
    this.editor = editor;
    this.viewContainerRef = viewContainerRef || null;

    return () => {
      this.cleanup();
    };
  }

  /**
   * Initialize the plugin with configuration
   */
  initialize(config: TypeaheadMenuPluginConfig<TOption>): () => void {
    if (!this.editor) {
      throw new Error('Plugin must be registered before initialization');
    }

    this.config = config;

    // Register update listener
    const unregisterUpdate = this.editor.registerUpdateListener(() => {
      this.updateListener();
    });

    // Register editable listener
    const unregisterEditable = this.editor.registerEditableListener((isEditable) => {
      if (!isEditable) {
        this.closeTypeahead();
      }
    });

    // Register keyboard commands
    const unregisterArrowDown = this.editor.registerCommand(
      KEY_ARROW_DOWN_COMMAND,
      (event: KeyboardEvent) => {
        if (this.resolution !== null) {
          event.preventDefault();
          this.handleArrowDown();
          return true;
        }
        return false;
      },
      config.commandPriority || COMMAND_PRIORITY_LOW,
    );

    const unregisterArrowUp = this.editor.registerCommand(
      KEY_ARROW_UP_COMMAND,
      (event: KeyboardEvent) => {
        if (this.resolution !== null) {
          event.preventDefault();
          this.handleArrowUp();
          return true;
        }
        return false;
      },
      config.commandPriority || COMMAND_PRIORITY_LOW,
    );

    const unregisterEnter = this.editor.registerCommand(
      KEY_ENTER_COMMAND,
      (event: KeyboardEvent) => {
        if (this.resolution !== null && this.config) {
          const options = this.config.options();
          if (options.length > 0) {
            event.preventDefault();
            this.selectOption(options[this.getSelectedIndex()]);
            return true;
          }
        }
        return false;
      },
      config.commandPriority || COMMAND_PRIORITY_LOW,
    );

    const unregisterEscape = this.editor.registerCommand(
      KEY_ESCAPE_COMMAND,
      () => {
        if (this.resolution !== null) {
          this.closeTypeahead();
          return true;
        }
        return false;
      },
      config.commandPriority || COMMAND_PRIORITY_LOW,
    );

    const unregisterTab = this.editor.registerCommand(
      KEY_TAB_COMMAND,
      (event: KeyboardEvent) => {
        if (this.resolution !== null && this.config) {
          const options = this.config.options();
          if (options.length > 0) {
            event.preventDefault();
            this.selectOption(options[this.getSelectedIndex()]);
            return true;
          }
        }
        return false;
      },
      config.commandPriority || COMMAND_PRIORITY_LOW,
    );

    this.unregisterListeners = [
      unregisterUpdate,
      unregisterEditable,
      unregisterArrowDown,
      unregisterArrowUp,
      unregisterEnter,
      unregisterEscape,
      unregisterTab,
    ];

    // Cleanup on destroy
    this.destroyRef.onDestroy(() => {
      this.cleanup();
    });

    return () => {
      this.cleanup();
    };
  }

  private updateListener(): void {
    if (!this.editor) return;
    this.editor.getEditorState().read(() => {
      if (!this.editor || !this.config) return;
      if (!this.editor.isEditable()) {
        this.closeTypeahead();
        return;
      }

      if (this.editor.isComposing()) {
        return;
      }

      const editorWindow = (this.editor as any)._window || window;
      const range = editorWindow.document.createRange();
      const selection = $getSelection();
      const text = getQueryTextForSearch(this.editor);

      if (
        !$isRangeSelection(selection) ||
        !selection.isCollapsed() ||
        text === null ||
        range === null
      ) {
        this.closeTypeahead();
        return;
      }

      const match = this.config.triggerFn(text, this.editor);
      this.config.onQueryChange(match ? match.matchingString : null);

      if (
        match !== null &&
        (this.config.ignoreEntityBoundary ||
          !isSelectionOnEntityBoundary(this.editor, match.leadOffset))
      ) {
        const isRangePositioned = tryToPositionRange(match.leadOffset, range, editorWindow);
        if (isRangePositioned) {
          const options = this.config.options();
          if (options.length > 0) {
            // Update existing menu or create new one
            if (this.resolution !== null && this.menuComponentRef) {
              // Update component with new options
              this.updateMenuComponent();
              // Update position
              const rect = range.getBoundingClientRect();
              if (this.overlayRef) {
                (this.overlayRef as any)._positionStrategy?.setOrigin({
                  x: rect.left,
                  y: rect.bottom,
                });
              }
            } else {
              this.openTypeahead({
                getRect: () => range.getBoundingClientRect(),
                match,
              });
            }
          } else {
            this.closeTypeahead();
          }
          return;
        }
      }
      this.closeTypeahead();
    });
  }

  private openTypeahead(resolution: MenuResolution): void {
    if (!this.config || !this.viewContainerRef) return;

    this.resolution = resolution;

    // Reset selected index
    const options = this.config.options();
    this.selectedIndexSignal.set(this.config.preselectFirstItem && options.length > 0 ? 0 : -1);

    if (this.config.onOpen) {
      this.config.onOpen(resolution);
    }

    this.createMenu();
  }

  private closeTypeahead(): void {
    if (this.resolution !== null && this.config && this.config.onClose) {
      this.config.onClose();
    }

    this.resolution = null;
    this.destroyMenu();
  }

  private createMenu(): void {
    if (!this.config || !this.viewContainerRef || !this.resolution) return;

    const rect = this.resolution.getRect();
    const positionStrategy = this.overlay
      .position()
      .flexibleConnectedTo({ x: rect.left, y: rect.bottom })
      .withPositions([
        { originX: 'start', originY: 'bottom', overlayX: 'start', overlayY: 'top' },
        { originX: 'start', originY: 'top', overlayX: 'start', overlayY: 'bottom' },
      ])
      .withDefaultOffsetY(4);

    const config: OverlayConfig = {
      positionStrategy,
      scrollStrategy: this.overlay.scrollStrategies.reposition(),
      panelClass: 'te-typeahead-menu-panel',
      backdropClass: 'cdk-overlay-transparent-backdrop',
      hasBackdrop: false,
    };

    this.overlayRef = this.overlay.create(config);

    // Use MentionAutocompleteComponent by default, or custom component
    const componentType = this.config.menuComponent || MentionAutocompleteComponent;
    const portal = new ComponentPortal(componentType, this.viewContainerRef);
    this.menuComponentRef = this.overlayRef.attach(portal);

    // Set up component inputs and outputs
    this.updateMenuComponent();

    // Create effect to listen to options signal changes
    const optionsEffect = effect(
      () => {
        // Read the options signal to track changes
        const options = this.config?.options();
        if (this.menuComponentRef?.instance) {
          this.updateMenuComponent();
        }
      },
      { injector: this.injector },
    );

    // Store cleanup function
    this.optionsEffectCleanup = () => {
      optionsEffect.destroy();
    };
  }

  private destroyMenu(): void {
    // Clean up options effect
    if (this.optionsEffectCleanup) {
      this.optionsEffectCleanup();
      this.optionsEffectCleanup = null;
    }

    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
    }
    this.menuComponentRef = null;
  }

  private selectedIndexSignal = signal<number>(-1);

  private updateMenuComponent(): void {
    if (!this.config || !this.menuComponentRef?.instance) return;

    const options = this.config.options();

    // Update options input
    if ('options' in this.menuComponentRef.instance) {
      this.menuComponentRef.setInput('options', options);
    }

    // Update selectedIndex input
    if ('selectedIndex' in this.menuComponentRef.instance) {
      const currentIndex = this.selectedIndexSignal();
      const maxIndex = options.length - 1;
      const clampedIndex = Math.max(0, Math.min(currentIndex, maxIndex));
      this.menuComponentRef.setInput(
        'selectedIndex',
        this.config.preselectFirstItem ? clampedIndex : -1,
      );
    }

    // Set up output subscription if not already done
    if (
      'selectOption' in this.menuComponentRef.instance &&
      !this.menuComponentRef.instance._subscription
    ) {
      this.menuComponentRef.instance._subscription =
        this.menuComponentRef.instance.selectOption.subscribe((option: TOption) => {
          this.selectOption(option);
        });
    }

    this.menuComponentRef.changeDetectorRef.detectChanges();
  }

  private getSelectedIndex(): number {
    return this.selectedIndexSignal();
  }

  private setSelectedIndex(index: number): void {
    if (!this.config) return;

    const options = this.config.options();
    const maxIndex = options.length - 1;
    const clampedIndex = Math.max(0, Math.min(index, maxIndex));
    this.selectedIndexSignal.set(this.config.preselectFirstItem ? clampedIndex : -1);

    // Update the component
    if (this.menuComponentRef?.instance && 'selectedIndex' in this.menuComponentRef.instance) {
      this.menuComponentRef.instance.selectedIndex = this.selectedIndexSignal();
      this.menuComponentRef.changeDetectorRef.detectChanges();
    }
  }

  private handleArrowDown(): void {
    const currentIndex = this.getSelectedIndex();
    this.setSelectedIndex(currentIndex + 1);
  }

  private handleArrowUp(): void {
    const currentIndex = this.getSelectedIndex();
    this.setSelectedIndex(currentIndex - 1);
  }

  private selectOption(option: TOption): void {
    if (!this.config || !this.editor) return;

    let textNodeContainingQuery: TextNode | null = null;

    this.editor.getEditorState().read(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        const anchorNode = selection.anchor.getNode();
        if ($isTextNode(anchorNode)) {
          textNodeContainingQuery = anchorNode;
        }
      }
    });

    const matchingString = this.resolution?.match.matchingString || '';

    this.config.onSelectOption(
      option,
      textNodeContainingQuery,
      () => this.closeTypeahead(),
      matchingString,
    );
  }

  private cleanup(): void {
    this.closeTypeahead();
    this.unregisterListeners.forEach((unregister) => unregister());
    this.unregisterListeners = [];
    this.config = null;
    this.editor = null;
    this.viewContainerRef = null;
  }
}
