import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProjectDetailPage } from './project-detail-page';
import { ProjectService } from '../../../../application/services/project.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { Modal, ToastService } from 'shared-ui';
import { TranslateModule } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';
import { of, BehaviorSubject } from 'rxjs';
import { signal } from '@angular/core';

describe('ProjectDetailPage', () => {
  let component: ProjectDetailPage;
  let fixture: ComponentFixture<ProjectDetailPage>;
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
      currentTab: signal('issues'),
      updateQueryParams: vi.fn(),
      navigateToOrganizationProjects: vi.fn(),
      navigateToOrganizations: vi.fn(),
    };

    modal = {
      open: vi.fn(),
      close: vi.fn(),
    };

    toast = {
      success: vi.fn(),
      error: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [ProjectDetailPage, TranslateModule.forRoot()],
      providers: [
        { provide: ProjectService, useValue: projectService },
        { provide: OrganizationService, useValue: organizationService },
        { provide: NavigationService, useValue: navigationService },
        { provide: Modal, useValue: modal },
        { provide: ToastService, useValue: toast },
        {
          provide: ActivatedRoute,
          useValue: {
            queryParams: of({}),
            snapshot: { queryParams: {} },
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProjectDetailPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display project info', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.project-detail-page_title')?.textContent).toContain(
      'Test Project',
    );
    expect(compiled.querySelector('.project-detail-page_key')?.textContent).toContain('TEST');
  });

  it('should handle tab navigation', () => {
    component.setActiveTab('board');
    expect(navigationService.updateQueryParams).toHaveBeenCalledWith({ tab: 'board' });
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
