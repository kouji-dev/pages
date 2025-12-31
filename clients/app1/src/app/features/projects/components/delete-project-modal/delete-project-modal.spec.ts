import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DeleteProjectModal } from './delete-project-modal';
import { ProjectService } from '../../../../application/services/project.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { Modal, ToastService } from 'shared-ui';
import { TranslateModule } from '@ngx-translate/core';
import { signal } from '@angular/core';

describe('DeleteProjectModal', () => {
  let component: DeleteProjectModal;
  let fixture: ComponentFixture<DeleteProjectModal>;
  let projectService: any;
  let organizationService: any;
  let navigationService: any;
  let modal: any;
  let toast: any;

  beforeEach(async () => {
    projectService = {
      deleteProject: vi.fn(),
    };

    organizationService = {
      currentOrganization: vi.fn().mockReturnValue({ id: 'org1' }),
    };

    navigationService = {
      navigateToOrganizationProjects: vi.fn(),
      navigateToOrganizations: vi.fn(),
    };

    modal = {
      close: vi.fn(),
    };

    toast = {
      success: vi.fn(),
      error: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [DeleteProjectModal, TranslateModule.forRoot()],
      providers: [
        { provide: ProjectService, useValue: projectService },
        { provide: OrganizationService, useValue: organizationService },
        { provide: NavigationService, useValue: navigationService },
        { provide: Modal, useValue: modal },
        { provide: ToastService, useValue: toast },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DeleteProjectModal);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('projectId', '1');
    fixture.componentRef.setInput('projectName', 'Test Project');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it("should not delete if confirmation name doesn't match", async () => {
    component.confirmationName.set('Wrong Name');
    await component.handleDelete();
    expect(projectService.deleteProject).not.toHaveBeenCalled();
  });

  it('should delete if confirmation name matches', async () => {
    component.confirmationName.set('Test Project');
    await component.handleDelete();
    expect(projectService.deleteProject).toHaveBeenCalledWith('1');
    expect(toast.success).toHaveBeenCalled();
    expect(modal.close).toHaveBeenCalled();
  });
});
