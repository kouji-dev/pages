import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProjectSettingsPage } from './project-settings-page';
import { ProjectService } from '../../../../application/services/project.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { Modal, ToastService } from 'shared-ui';
import { TranslateModule } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { signal } from '@angular/core';

describe('ProjectSettingsPage', () => {
  let component: ProjectSettingsPage;
  let fixture: ComponentFixture<ProjectSettingsPage>;
  let projectService: any;
  let organizationService: any;
  let navigationService: any;
  let modal: any;
  let toast: any;

  const mockProject = {
    id: '1',
    name: 'Test Project',
    key: 'TEST',
    description: 'Test Description',
    organizationId: 'org1',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
    memberCount: 5,
  };

  beforeEach(async () => {
    projectService = {
      currentProject: signal(mockProject),
      isFetchingProject: signal(false),
      hasProjectError: signal(false),
      projectError: signal(null),
      fetchProject: vi.fn(),
      updateProject: vi.fn().mockResolvedValue(undefined),
      deleteProject: vi.fn().mockResolvedValue(undefined),
    };

    organizationService = {
      currentOrganization: signal({ id: 'org1', name: 'Org 1' }),
    };

    navigationService = {
      currentOrganizationId: signal('org1'),
      currentProjectId: signal('1'),
      navigateToOrganizationProjects: vi.fn(),
    };

    modal = {
      open: vi.fn(),
    };

    toast = {
      success: vi.fn(),
      error: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [ProjectSettingsPage, TranslateModule.forRoot()],
      providers: [
        { provide: ProjectService, useValue: projectService },
        { provide: OrganizationService, useValue: organizationService },
        { provide: NavigationService, useValue: navigationService },
        { provide: Modal, useValue: modal },
        { provide: ToastService, useValue: toast },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: { paramMap: { get: () => '1' } },
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProjectSettingsPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize form with project data', () => {
    expect(component.name()).toBe('Test Project');
    expect(component.key()).toBe('TEST');
  });

  it('should handle save project', async () => {
    component.name.set('New Name');
    await component.handleSaveProject();
    expect(projectService.updateProject).toHaveBeenCalledWith('1', {
      name: 'New Name',
      description: 'Test Description',
    });
    expect(toast.success).toHaveBeenCalled();
  });
});
