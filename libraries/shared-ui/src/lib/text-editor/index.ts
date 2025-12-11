/*
 * Public API exports for text-editor module
 */

// Main component
export { TextEditor } from './text-editor';

// Attachment service interfaces and helpers
export type {
  TextEditorAttachmentServiceInterface,
  AttachmentMetadata,
} from './interfaces/attachment-service.interface';
export {
  provideAttachmentService,
  injectAttachmentService,
} from './interfaces/attachment-service.interface';

// Mention list provider interfaces and helpers
export type {
  TextEditorMentionListProviderInterface,
  MentionOption,
} from './interfaces/mention-list-provider.interface';
export {
  provideMentionListProvider,
  injectMentionListProvider,
} from './interfaces/mention-list-provider.interface';
