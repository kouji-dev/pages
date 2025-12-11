import { Injectable, inject, ViewContainerRef, signal, effect } from '@angular/core';
import {
  LexicalEditor,
  $getSelection,
  $isRangeSelection,
  TextNode,
  $isTextNode,
  $createTextNode,
} from 'lexical';
import { TextEditorPlugin } from './plugin';
import { $createMentionNode } from '../nodes/mention-node';
import type {
  TextEditorMentionListProviderInterface,
  MentionOption,
} from '../interfaces/mention-list-provider.interface';
import { injectMentionListProvider } from '../interfaces/mention-list-provider.interface';
import {
  TypeaheadMenuPlugin,
  createBasicTypeaheadTriggerMatch,
  type MenuOption,
} from './typeahead-menu-plugin';

/**
 * Plugin for handling @mention autocomplete
 * Adapted from Lexical React MentionsPlugin
 */
@Injectable()
export class MentionPlugin implements TextEditorPlugin {
  private readonly mentionProvider = injectMentionListProvider();
  private readonly typeaheadPlugin = inject(TypeaheadMenuPlugin<MentionMenuOption>);
  private editor: LexicalEditor | null = null;
  private viewContainerRef: ViewContainerRef | null = null;
  private unregisterTypeahead: (() => void) | null = null;
  private queryString = signal<string>('');
  private options = signal<MentionMenuOption[]>([]);

  register(
    editor: LexicalEditor,
    rootElement?: HTMLElement,
    viewContainerRef?: ViewContainerRef,
  ): () => void {
    this.editor = editor;
    this.viewContainerRef = viewContainerRef || null;

    // Register the typeahead plugin
    const unregisterTypeahead = this.typeaheadPlugin.register(
      editor,
      rootElement,
      viewContainerRef,
    );

    // Initialize typeahead with configuration
    const unregisterInit = this.typeaheadPlugin.initialize({
      triggerFn: createBasicTypeaheadTriggerMatch('@', {
        minLength: 0,
        maxLength: 75,
        allowWhitespace: false,
      }),
      onQueryChange: (matchingString) => {
        this.queryString.set(matchingString || '');
        if (matchingString !== null) {
          this.searchMentions(matchingString);
        } else {
          this.options.set([]);
        }
      },
      onSelectOption: (option, textNodeContainingQuery, closeMenu, matchingString) => {
        this.selectMention(option, textNodeContainingQuery, matchingString);
        closeMenu();
      },
      options: this.options.asReadonly(),
      preselectFirstItem: true,
      ignoreEntityBoundary: false,
    });

    this.unregisterTypeahead = () => {
      unregisterTypeahead();
      unregisterInit();
    };

    return () => {
      this.cleanup();
    };
  }

  private async searchMentions(query: string): Promise<void> {
    try {
      const results = await this.mentionProvider.searchMentions(query);
      const menuOptions: MentionMenuOption[] = results.map((result) => ({
        key: result.id,
        ...result,
      }));
      this.options.set(menuOptions);
    } catch (error) {
      console.error('Failed to search mentions:', error);
      this.options.set([]);
    }
  }

  private selectMention(
    option: MentionMenuOption,
    textNodeContainingQuery: TextNode | null,
    matchingString: string,
  ): void {
    if (!this.editor) return;

    this.editor.update(() => {
      const mentionNode = $createMentionNode({
        mentionId: option.id,
        mentionLabel: option.label,
      });

      // Replace the query text with the mention node
      if (textNodeContainingQuery) {
        const textContent = textNodeContainingQuery.getTextContent();
        const selection = $getSelection();
        if (!$isRangeSelection(selection)) return;

        const anchorOffset = selection.anchor.offset;
        const queryString = '@' + matchingString;
        const mentionStart = textContent.lastIndexOf(queryString, anchorOffset);

        if (mentionStart >= 0) {
          const beforeText = textContent.slice(0, mentionStart);
          const queryEnd = mentionStart + queryString.length;
          const afterText = textContent.slice(queryEnd);

          // Split the node at the mention start
          if (beforeText) {
            const [beforeNode, queryNode] = textNodeContainingQuery.splitText(mentionStart);
            // Split again at the end of the query
            if (queryNode) {
              queryNode.splitText(queryString.length);
              // Replace the query node with the mention node
              queryNode.replace(mentionNode);
              // Handle text after the mention
              if (afterText) {
                mentionNode.insertAfter($createTextNode(afterText));
              }
              mentionNode.selectNext();
            }
          } else {
            // No text before, split at the end of query
            const [queryNode] = textNodeContainingQuery.splitText(queryString.length);
            queryNode.replace(mentionNode);
            if (afterText) {
              mentionNode.insertAfter($createTextNode(afterText));
            }
            mentionNode.selectNext();
          }
        } else {
          // Fallback: just replace the entire node
          textNodeContainingQuery.replace(mentionNode);
          mentionNode.selectNext();
        }
      }
    });
  }

  private cleanup(): void {
    if (this.unregisterTypeahead) {
      this.unregisterTypeahead();
      this.unregisterTypeahead = null;
    }
    this.editor = null;
    this.viewContainerRef = null;
    this.options.set([]);
    this.queryString.set('');
  }
}

interface MentionMenuOption extends MenuOption {
  id: string;
  label: string;
  avatarUrl?: string;
}
