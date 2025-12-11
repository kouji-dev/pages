/**
 * Props for AttachmentNode
 */
export interface AttachmentNodeProps {
  attachmentId: string;
}

/**
 * Props for ImageNode
 */
export interface ImageNodeProps {
  src: string;
  alt?: string;
  width?: number;
  height?: number;
}

/**
 * Props for MentionNode
 */
export interface MentionNodeProps {
  mentionId: string;
  mentionLabel: string;
}
