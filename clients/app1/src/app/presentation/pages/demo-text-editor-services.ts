import type { TextEditorAttachmentServiceInterface, AttachmentMetadata } from 'shared-ui';
import type { TextEditorMentionListProviderInterface, MentionOption } from 'shared-ui';

/**
 * Dummy in-memory implementation of attachment service for demo purposes
 */
export class DemoAttachmentService implements TextEditorAttachmentServiceInterface {
  private attachments = new Map<string, AttachmentMetadata>();
  private files = new Map<string, File>();
  private nextId = 1;

  getNextId(): string {
    return `attachment-${this.nextId++}`;
  }

  async upload(file: File): Promise<string> {
    // Simulate upload delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Generate a new ID for the uploaded file
    const id = this.getNextId();

    // Store the file and attachment metadata
    this.files.set(id, file);
    this.attachments.set(id, {
      id,
      filename: file.name,
      mimeType: file.type || 'application/octet-stream',
      fileSize: file.size,
    });

    return id;
  }

  async getAttachmentMetadata(id: string): Promise<AttachmentMetadata | null> {
    return this.attachments.get(id) || null;
  }

  async download(attachmentId: string): Promise<void> {
    const file = this.files.get(attachmentId);
    if (!file) {
      throw new Error(`Attachment with ID ${attachmentId} not found`);
    }

    // Create a blob URL from the stored file
    const blobUrl = URL.createObjectURL(file);

    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up the blob URL after a short delay
    setTimeout(() => {
      URL.revokeObjectURL(blobUrl);
    }, 100);
  }

  async deleteAttachment(id: string): Promise<void> {
    this.attachments.delete(id);
    this.files.delete(id);
  }

  async canDeleteAttachment(id: string): Promise<boolean> {
    return this.attachments.has(id);
  }
}

/**
 * Dummy in-memory implementation of mention list provider for demo purposes
 */
export class DemoMentionListProvider implements TextEditorMentionListProviderInterface {
  private readonly users: MentionOption[] = [
    { id: 'john-doe', label: 'John Doe', avatarUrl: undefined },
    { id: 'jane-smith', label: 'Jane Smith', avatarUrl: undefined },
    { id: 'bob-johnson', label: 'Bob Johnson', avatarUrl: undefined },
    { id: 'alice-williams', label: 'Alice Williams', avatarUrl: undefined },
    { id: 'charlie-brown', label: 'Charlie Brown', avatarUrl: undefined },
    { id: 'diana-prince', label: 'Diana Prince', avatarUrl: undefined },
    { id: 'eve-adams', label: 'Eve Adams', avatarUrl: undefined },
    { id: 'frank-miller', label: 'Frank Miller', avatarUrl: undefined },
  ];

  async searchMentions(query: string): Promise<MentionOption[]> {
    const lowerQuery = query.toLowerCase();
    return this.users.filter(
      (user) => user.label.toLowerCase().includes(lowerQuery) || user.id.includes(lowerQuery),
    );
  }
}
