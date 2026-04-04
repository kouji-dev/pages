import {
  Component,
  ChangeDetectionStrategy,
  computed,
  effect,
  inject,
  input,
  model,
  signal,
} from '@angular/core';
import {
  Modal,
  ModalContainer,
  ModalHeader,
  ModalContent,
  ModalFooter,
  Button,
  Select,
  SelectOption,
  ToastService,
} from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import {
  BoardService,
  BoardListType,
  CreateBoardListRequest,
} from '../../../../application/services/board.service';
import { Label } from '../../../../application/services/label.service';
import { ProjectMember } from '../../../../application/services/project-members.service';
import { SprintService, SprintResponse } from '../../../../application/services/sprint.service';

@Component({
  selector: 'app-add-board-column-modal',
  standalone: true,
  imports: [ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Select, TranslatePipe],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{ 'board.addColumn.title' | translate }}</lib-modal-header>
      <lib-modal-content>
        <div class="add-board-column-form">
          <lib-select
            [label]="'board.addColumn.columnType' | translate"
            [options]="listTypeOptions()"
            [(model)]="listTypeModel"
            [placeholder]="'board.addColumn.selectType' | translate"
          />
          @if (listTypeModel() === 'label') {
            <lib-select
              [label]="'board.addColumn.label' | translate"
              [options]="labelOptions()"
              [(model)]="labelIdModel"
              [placeholder]="'board.addColumn.selectLabel' | translate"
            />
            @if (labels().length === 0) {
              <p class="add-board-column-form_hint">{{ 'board.addColumn.noLabels' | translate }}</p>
            }
          }
          @if (listTypeModel() === 'assignee') {
            <lib-select
              [label]="'board.assignee' | translate"
              [options]="assigneeOptions()"
              [(model)]="userIdModel"
              [placeholder]="'board.addColumn.selectMember' | translate"
            />
          }
          @if (listTypeModel() === 'milestone') {
            @if (isLoadingSprints()) {
              <p class="add-board-column-form_hint">
                {{ 'board.addColumn.loadingSprints' | translate }}
              </p>
            } @else if (sprints().length === 0) {
              <p class="add-board-column-form_hint">
                {{ 'board.addColumn.noSprints' | translate }}
              </p>
            } @else {
              <lib-select
                [label]="'board.addColumn.sprint' | translate"
                [options]="sprintOptions()"
                [(model)]="sprintIdModel"
                [placeholder]="'board.addColumn.selectSprint' | translate"
              />
            }
          }
        </div>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isSubmitting()">
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button
          variant="primary"
          (clicked)="handleSubmit()"
          [loading]="isSubmitting()"
          [disabled]="!canSubmit()"
        >
          {{ 'board.addColumn.submit' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .add-board-column-form {
        @apply flex flex-col gap-4;
      }

      .add-board-column-form_hint {
        @apply text-sm text-muted-foreground;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddBoardColumnModal {
  private readonly modal = inject(Modal);
  private readonly boardService = inject(BoardService);
  private readonly sprintService = inject(SprintService);
  private readonly toast = inject(ToastService);
  private readonly translate = inject(TranslateService);

  readonly boardId = input.required<string>();
  readonly projectId = input.required<string>();
  readonly labels = input<Label[]>([]);
  readonly members = input<ProjectMember[]>([]);

  readonly listTypeModel = model<BoardListType>('label');
  readonly labelIdModel = model<string | null>(null);
  readonly userIdModel = model<string | null>(null);
  readonly sprintIdModel = model<string | null>(null);

  readonly sprints = signal<SprintResponse[]>([]);
  readonly isLoadingSprints = signal(false);
  readonly isSubmitting = signal(false);

  constructor() {
    effect(() => {
      this.listTypeModel();
      this.labelIdModel.set(null);
      this.userIdModel.set(null);
      this.sprintIdModel.set(null);
    });

    effect(() => {
      const projectId = this.projectId();
      const listType = this.listTypeModel();
      if (!projectId || listType !== 'milestone') return;
      void this.loadSprints(projectId);
    });
  }

  readonly listTypeOptions = computed<SelectOption<BoardListType>[]>(() => [
    { value: 'label', label: this.translate.instant('board.addColumn.typeLabel') },
    { value: 'assignee', label: this.translate.instant('board.addColumn.typeAssignee') },
    { value: 'milestone', label: this.translate.instant('board.addColumn.typeMilestone') },
  ]);

  readonly labelOptions = computed<SelectOption<string>[]>(() =>
    this.labels().map((l) => ({ value: l.id, label: l.name })),
  );

  readonly assigneeOptions = computed<SelectOption<string>[]>(() =>
    this.members().map((m) => ({ value: m.user_id, label: m.user_name })),
  );

  readonly sprintOptions = computed<SelectOption<string>[]>(() =>
    this.sprints().map((s) => ({
      value: s.id,
      label: `${s.name} (${this.translate.instant(`sprints.status.${s.status}`)})`,
    })),
  );

  readonly canSubmit = computed(() => {
    const t = this.listTypeModel();
    if (t === 'label') {
      return !!this.labelIdModel() && this.labels().length > 0;
    }
    if (t === 'assignee') {
      return !!this.userIdModel();
    }
    if (t === 'milestone') {
      return !!this.sprintIdModel() && this.sprints().length > 0 && !this.isLoadingSprints();
    }
    return false;
  });

  private async loadSprints(projectId: string): Promise<void> {
    this.isLoadingSprints.set(true);
    try {
      const res = await this.sprintService.listProjectSprints(projectId, { page: 1, limit: 100 });
      this.sprints.set(res.sprints ?? []);
    } catch {
      this.sprints.set([]);
      this.toast.error(this.translate.instant('board.addColumn.failedToLoadSprints'));
    } finally {
      this.isLoadingSprints.set(false);
    }
  }

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    if (!this.canSubmit()) return;

    const listType = this.listTypeModel();
    let list_config: Record<string, unknown>;

    if (listType === 'label') {
      const id = this.labelIdModel();
      if (!id) return;
      list_config = { label_id: id };
    } else if (listType === 'assignee') {
      const id = this.userIdModel();
      if (!id) return;
      list_config = { user_id: id };
    } else {
      const id = this.sprintIdModel();
      if (!id) return;
      list_config = { sprint_id: id };
    }

    const request: CreateBoardListRequest = { list_type: listType, list_config };
    this.isSubmitting.set(true);
    try {
      await this.boardService.createBoardList(this.boardId(), request);
      this.modal.close(true);
    } catch {
      this.toast.error(this.translate.instant('board.addColumn.failedToCreate'));
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
