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
import { ImageDecoratorComponent } from '../decorators/image-decorator.component';
import type { DecoratorNodeComponentType } from './decorator-node-types';
import type { ImageNodeProps } from './node-props';

export type SerializedImageNode = Spread<ImageNodeProps, SerializedLexicalNode>;

function $convertImageElement(domNode: HTMLElement): DOMConversionOutput | null {
  const src = domNode.getAttribute('data-lexical-image-src') || domNode.getAttribute('src');
  const alt = domNode.getAttribute('data-lexical-image-alt') || domNode.getAttribute('alt') || '';
  const width = domNode.getAttribute('data-lexical-image-width')
    ? parseInt(domNode.getAttribute('data-lexical-image-width') || '0', 10)
    : undefined;
  const height = domNode.getAttribute('data-lexical-image-height')
    ? parseInt(domNode.getAttribute('data-lexical-image-height') || '0', 10)
    : undefined;

  if (src) {
    const props: ImageNodeProps = { src, alt: alt || undefined, width, height };
    const node = $createImageNode(props);
    return { node };
  }
  return null;
}

export class ImageNode extends DecoratorNode<DecoratorNodeComponentType<ImageDecoratorComponent>> {
  __props: ImageNodeProps;

  static override getType(): string {
    return 'image';
  }

  static override clone(node: ImageNode): ImageNode {
    return new ImageNode(node.__props, node.__key);
  }

  static override importJSON(serializedNode: SerializedImageNode): ImageNode {
    return $createImageNode(serializedNode).updateFromJSON(serializedNode);
  }

  constructor(props: ImageNodeProps | string = { src: '' }, key?: NodeKey) {
    super(key);
    // Support both object and string (src) for backward compatibility
    this.__props = typeof props === 'string' ? { src: props } : props;
  }

  override exportJSON(): SerializedImageNode {
    return {
      ...super.exportJSON(),
      ...this.__props,
    };
  }

  override createDOM(): HTMLElement {
    const element = document.createElement('div');
    element.className = 'te-image';
    element.setAttribute('data-lexical-key', this.getKey());
    element.setAttribute('data-lexical-image', 'true');
    element.setAttribute('data-lexical-image-src', this.__props.src);
    element.setAttribute('data-lexical-image-alt', this.__props.alt || '');
    element.contentEditable = 'false';
    return element;
  }

  override updateDOM(): false {
    // Decorator nodes handle their own updates via Angular components
    return false;
  }

  override decorate(): DecoratorNodeComponentType<ImageDecoratorComponent> {
    // Return the Angular component class that will be rendered
    return ImageDecoratorComponent;
  }

  override exportDOM(): DOMExportOutput {
    const element = document.createElement('img');
    element.setAttribute('data-lexical-key', this.getKey());
    element.setAttribute('data-lexical-image', 'true');
    element.setAttribute('data-lexical-image-src', this.__props.src);
    element.setAttribute('data-lexical-image-alt', this.__props.alt || '');
    element.src = this.__props.src;
    element.alt = this.__props.alt || '';
    if (this.__props.width) {
      element.setAttribute('data-lexical-image-width', this.__props.width.toString());
      element.width = this.__props.width;
    }
    if (this.__props.height) {
      element.setAttribute('data-lexical-image-height', this.__props.height.toString());
      element.height = this.__props.height;
    }
    return { element };
  }

  static override importDOM(): DOMConversionMap | null {
    return {
      img: (domNode: HTMLElement) => {
        if (!domNode.hasAttribute('data-lexical-image') && !domNode.hasAttribute('src')) {
          return null;
        }
        return {
          conversion: $convertImageElement,
          priority: 1,
        };
      },
    };
  }

  getProps(): ImageNodeProps {
    return this.__props;
  }

  getSrc(): string {
    return this.__props.src;
  }

  getAlt(): string {
    return this.__props.alt || '';
  }

  getWidth(): number {
    return this.__props.width || 0;
  }

  getHeight(): number {
    return this.__props.height || 0;
  }

  setAlt(alt: string): this {
    const self = this.getWritable();
    self.__props = { ...self.__props, alt };
    return self;
  }

  setWidth(width: number): this {
    const self = this.getWritable();
    self.__props = { ...self.__props, width };
    return self;
  }

  setHeight(height: number): this {
    const self = this.getWritable();
    self.__props = { ...self.__props, height };
    return self;
  }
}

/**
 * Create an image node
 */
export function $createImageNode(
  props: ImageNodeProps | string,
  alt?: string,
  width?: number,
  height?: number,
): ImageNode {
  // Support both object and individual parameters for backward compatibility
  const nodeProps: ImageNodeProps =
    typeof props === 'string' ? { src: props, alt: alt || undefined, width, height } : props;
  const imageNode = new ImageNode(nodeProps);
  return $applyNodeReplacement(imageNode);
}

/**
 * Check if a node is an ImageNode
 */
export function $isImageNode(node: LexicalNode | null | undefined): node is ImageNode {
  return node instanceof ImageNode;
}
