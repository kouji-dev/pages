import {
  $applyNodeReplacement,
  type DOMConversionMap,
  type DOMConversionOutput,
  type DOMExportOutput,
  type EditorConfig,
  type LexicalNode,
  type NodeKey,
  type SerializedLexicalNode,
  type Spread,
  DecoratorNode,
} from 'lexical';
import { AttachmentDecoratorComponent } from '../decorators/attachment-decorator.component';
import type { DecoratorNodeComponentType } from './decorator-node-types';
import type { AttachmentNodeProps } from './node-props';

export type SerializedAttachmentNode = Spread<AttachmentNodeProps, SerializedLexicalNode>;

function $convertAttachmentElement(domNode: HTMLElement): DOMConversionOutput | null {
  const attachmentId = domNode.getAttribute('data-lexical-attachment-id');
  if (attachmentId) {
    const node = $createAttachmentNode(attachmentId);
    return { node };
  }
  return null;
}

export class AttachmentNode extends DecoratorNode<
  DecoratorNodeComponentType<AttachmentDecoratorComponent>
> {
  __props: AttachmentNodeProps;

  static override getType(): string {
    return 'attachment';
  }

  static override clone(node: AttachmentNode): AttachmentNode {
    return new AttachmentNode(node.__props, node.__key);
  }

  static override importJSON(serializedNode: SerializedAttachmentNode): AttachmentNode {
    return $createAttachmentNode(serializedNode.attachmentId).updateFromJSON(serializedNode);
  }

  constructor(props: AttachmentNodeProps | string = { attachmentId: '' }, key?: NodeKey) {
    super(key);
    // Support both object and string for backward compatibility
    this.__props = typeof props === 'string' ? { attachmentId: props } : props;
  }

  override exportJSON(): SerializedAttachmentNode {
    return {
      ...super.exportJSON(),
      ...this.__props,
    };
  }

  override createDOM(): HTMLElement {
    const element = document.createElement('div');
    element.className = 'te-attachment';
    element.setAttribute('data-lexical-key', this.getKey());
    element.setAttribute('data-lexical-attachment', 'true');
    element.setAttribute('data-lexical-attachment-id', this.__props.attachmentId);
    element.contentEditable = 'false';
    return element;
  }

  override updateDOM(): false {
    // Decorator nodes handle their own updates via Angular components
    return false;
  }

  override decorate(): DecoratorNodeComponentType<AttachmentDecoratorComponent> {
    // Return the Angular component class that will be rendered
    return AttachmentDecoratorComponent;
  }

  override exportDOM(): DOMExportOutput {
    const element = document.createElement('span');
    element.setAttribute('data-lexical-key', this.getKey());
    element.setAttribute('data-lexical-attachment', 'true');
    element.setAttribute('data-lexical-attachment-id', this.__props.attachmentId);
    return { element };
  }

  static override importDOM(): DOMConversionMap | null {
    return {
      span: (domNode: HTMLElement) => {
        if (!domNode.hasAttribute('data-lexical-attachment')) {
          return null;
        }
        return {
          conversion: $convertAttachmentElement,
          priority: 1,
        };
      },
    };
  }

  getProps(): AttachmentNodeProps {
    return this.__props;
  }

  getAttachmentId(): string {
    return this.__props.attachmentId;
  }
}

/**
 * Create an attachment node
 */
export function $createAttachmentNode(attachmentId: string | AttachmentNodeProps): AttachmentNode {
  const props = typeof attachmentId === 'string' ? { attachmentId } : attachmentId;
  const attachmentNode = new AttachmentNode(props);
  return $applyNodeReplacement(attachmentNode);
}

/**
 * Check if a node is an AttachmentNode
 */
export function $isAttachmentNode(node: LexicalNode | null | undefined): node is AttachmentNode {
  return node instanceof AttachmentNode;
}
