import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CreateProjectModal } from './create-project-modal';
import { ProjectService } from '../../../../application/services/project.service';
import {
  ToastService,
  Modal,
  ModalContainer,
  ModalHeader,
  ModalContent,
  ModalFooter,
  Button,
  Input,
} from 'shared-ui';
import { TranslateModule } from '@ngx-translate/core';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('CreateProjectModal', () => {
  let component: CreateProjectModal;
  let fixture: ComponentFixture<CreateProjectModal>;
  let projectService: ProjectService;
  let toastService: ToastService;
  let modal: Modal;

  beforeEach(async () => {
    const mockProjectService = {
      createProject: vi.fn(),
    };

    const mockToastService = {
      success: vi.fn(),
      error: vi.fn(),
    };

    const mockModal = {
      close: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [
        CreateProjectModal,
        TranslateModule.forRoot(),
        NoopAnimationsModule,
        ModalContainer,
        ModalHeader,
        ModalContent,
        ModalFooter,
        Button,
        Input,
      ],
      providers: [
        { provide: ProjectService, useValue: mockProjectService },
        { provide: ToastService, useValue: mockToastService },
        { provide: Modal, useValue: mockModal },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateProjectModal);
    component = fixture.componentInstance;
    projectService = TestBed.inject(ProjectService);
    toastService = TestBed.inject(ToastService);
    modal = TestBed.inject(Modal);

    // Set input
    fixture.componentRef.setInput('organizationId', 'org1');

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should validate project name - required', () => {
    component.name.set('');
    expect(component.nameError()).toBeTruthy();
    expect(component.isValid()).toBe(false);
  });

  it('should validate project name - min length', () => {
    component.name.set('AB');
    expect(component.nameError()).toBeTruthy();
    expect(component.isValid()).toBe(false);
  });

  it('should validate project name - valid', () => {
    component.name.set('Valid Project');
    expect(component.nameError()).toBe('');
    expect(component.isValid()).toBe(true);
  });

  it('should auto-generate key from name', () => {
    component.name.set('My Project');
    fixture.detectChanges(); // allow effect to run

    // Effects run asynchronously usually, but in tests often synchronously with detectChanges or whenStable.
    // However, effect() might need `TestBed.flushEffects()` or just wait.
    // Let's verify if effect runs.

    // In Angular signal effects run on next change detection or something.
    // Let's manually trigger change detection.
    fixture.detectChanges();

    expect(component.key()).toBe('MYPROJECT');
  });

  it('should call createProject on submit', async () => {
    component.name.set('New Project');
    fixture.detectChanges();

    vi.mocked(projectService.createProject).mockResolvedValue({
      id: '1',
      name: 'New Project',
      key: 'NEWPROJECT',
      organization_id: 'org1',
    } as any);

    await component.handleSubmit();

    expect(projectService.createProject).toHaveBeenCalledWith({
      name: 'New Project',
      key: 'NEWPROJECT', // Auto generated
      description: undefined,
      organization_id: 'org1',
    });
    expect(toastService.success).toHaveBeenCalled();
    expect(modal.close).toHaveBeenCalled();
  });

  it('should close modal on cancel', () => {
    component.handleCancel();
    expect(modal.close).toHaveBeenCalled();
  });
});
