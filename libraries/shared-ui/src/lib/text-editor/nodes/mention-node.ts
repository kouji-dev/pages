import {
  $applyNodeReplacement,
  type DOMConversionMap,
  type DOMConversionOutput,
  type DOMExportOutput,
  type EditorConfig,
  type LexicalNode,
  type NodeKey,
  type SerializedTextNode,
  type Spread,
  TextNode,
} from 'lexical';
import type { MentionNodeProps } from './node-props';

export type SerializedMentionNode = Spread<
  {
    mentionId: string;
    mentionLabel?: string;
  },
  SerializedTextNode
>;

function $convertMentionElement(domNode: HTMLElement): DOMConversionOutput | null {
  const textContent = domNode.textContent;
  const mentionId = domNode.getAttribute('data-lexical-mention-id');
  const mentionLabel = domNode.getAttribute('data-lexical-mention-label');

  if (textContent !== null) {
    const id = typeof mentionId === 'string' ? mentionId : textContent.replace('@', '');
    const label = typeof mentionLabel === 'string' ? mentionLabel : textContent.replace('@', '');
    const props: MentionNodeProps = { mentionId: id, mentionLabel: label };
    const node = $createMentionNode(props);
    return { node };
  }

  return null;
}

const mentionStyle = 'background-color: rgba(24, 119, 232, 0.2)';

export class MentionNode extends TextNode {
  __props: MentionNodeProps;

  static override getType(): string {
    return 'mention';
  }

  static override clone(node: MentionNode): MentionNode {
    return new MentionNode(node.__props, node.__text, node.__key);
  }

  static override importJSON(serializedNode: SerializedMentionNode): MentionNode {
    const props: MentionNodeProps = {
      mentionId: serializedNode.mentionId,
      mentionLabel: serializedNode.mentionLabel || serializedNode.mentionId,
    };
    return $createMentionNode(props).updateFromJSON(serializedNode);
  }

  constructor(props: MentionNodeProps, text?: string, key?: NodeKey) {
    super(text ?? '@' + props.mentionLabel, key);
    this.__props = props;
  }

  override exportJSON(): SerializedMentionNode {
    return {
      ...super.exportJSON(),
      ...this.__props,
    };
  }

  override createDOM(config: EditorConfig): HTMLElement {
    const dom = super.createDOM(config);
    dom.style.cssText = mentionStyle;
    dom.className = 'te-mention';
    dom.setAttribute('data-lexical-mention', 'true');
    dom.setAttribute('data-lexical-mention-id', this.__props.mentionId);
    dom.setAttribute('data-lexical-mention-label', this.__props.mentionLabel);
    dom.spellcheck = false;
    return dom;
  }

  override updateDOM(prevNode: this, dom: HTMLElement, config: EditorConfig): boolean {
    if (super.updateDOM(prevNode, dom, config)) {
      return true;
    }
    if (prevNode.__props.mentionId !== this.__props.mentionId) {
      dom.setAttribute('data-lexical-mention-id', this.__props.mentionId);
    }
    if (prevNode.__props.mentionLabel !== this.__props.mentionLabel) {
      dom.setAttribute('data-lexical-mention-label', this.__props.mentionLabel);
    }
    return false;
  }

  override exportDOM(): DOMExportOutput {
    const element = document.createElement('span');
    element.setAttribute('data-lexical-mention', 'true');
    element.setAttribute('data-lexical-mention-id', this.__props.mentionId);
    element.setAttribute('data-lexical-mention-label', this.__props.mentionLabel);
    element.textContent = this.__text;
    return { element };
  }

  static override importDOM(): DOMConversionMap | null {
    return {
      span: (domNode: HTMLElement) => {
        if (!domNode.hasAttribute('data-lexical-mention')) {
          return null;
        }
        return {
          conversion: $convertMentionElement,
          priority: 1,
        };
      },
    };
  }

  override isTextEntity(): true {
    return true;
  }

  override canInsertTextBefore(): boolean {
    return false;
  }

  override canInsertTextAfter(): boolean {
    return false;
  }

  getProps(): MentionNodeProps {
    return this.__props;
  }

  getMentionId(): string {
    return this.__props.mentionId;
  }

  getMentionLabel(): string {
    return this.__props.mentionLabel;
  }
}

/**
 * Create a mention node
 */
export function $createMentionNode(
  props: MentionNodeProps | string,
  mentionLabel?: string,
): MentionNode {
  // Support both object and individual parameters for backward compatibility
  const nodeProps: MentionNodeProps =
    typeof props === 'string' ? { mentionId: props, mentionLabel: mentionLabel || props } : props;
  const mentionNode = new MentionNode(nodeProps);
  mentionNode.setMode('segmented').toggleDirectionless();
  return $applyNodeReplacement(mentionNode);
}

/**
 * Check if a node is a MentionNode
 */
export function $isMentionNode(node: LexicalNode | null | undefined): node is MentionNode {
  return node instanceof MentionNode;
}
