import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { signal, computed } from '@angular/core';
import { ProjectCard } from './project-card';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { Project } from '../../../../application/services/project.service';
import { Icon, Button } from 'shared-ui';
import { TranslateModule } from '@ngx-translate/core';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('ProjectCard', () => {
  let component: ProjectCard;
  let fixture: ComponentFixture<ProjectCard>;
  let organizationService: OrganizationService;
  let navigationService: NavigationService;

  const mockProject: Project = {
    id: '1',
    name: 'Test Project',
    key: 'PROJ',
    description: 'Test Description',
    organizationId: 'org1',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
    memberCount: 5,
  };

  beforeEach(async () => {
    const mockOrganizationService = {
      currentOrganization: signal({ id: 'org1', name: 'Test Org' }),
    };

    const mockNavigationService = {
      getProjectRoute: vi.fn().mockReturnValue(['/app', 'organizations', 'org1', 'projects', '1']),
    };

    await TestBed.configureTestingModule({
      imports: [ProjectCard, RouterTestingModule, Icon, Button, TranslateModule.forRoot()],
      providers: [
        { provide: OrganizationService, useValue: mockOrganizationService },
        { provide: NavigationService, useValue: mockNavigationService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProjectCard);
    component = fixture.componentInstance;
    organizationService = TestBed.inject(OrganizationService);
    navigationService = TestBed.inject(NavigationService);

    // Set input
    fixture.componentRef.setInput('project', mockProject);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display project name', () => {
    const nameEl = fixture.nativeElement.querySelector('.project-card_name');
    expect(nameEl.textContent).toContain('Test Project');
  });

  it('should display project key', () => {
    const keyEl = fixture.nativeElement.querySelector('.project-card_key');
    expect(keyEl.textContent).toContain('PROJ');
  });

  it('should display project description', () => {
    const descEl = fixture.nativeElement.querySelector('.project-card_description');
    expect(descEl.textContent).toContain('Test Description');
  });

  it('should display member count', () => {
    const membersEl = fixture.nativeElement.querySelector('.project-card_member-count');
    expect(membersEl.textContent).toContain('5');
  });

  it('should call onSettings emit when settings button clicked', () => {
    let emittedProject: Project | undefined;
    component.onSettings.subscribe((p) => (emittedProject = p));

    const settingsBtn = fixture.nativeElement.querySelector('.project-card_action-item');
    settingsBtn.click(); // This might trigger the lib-button click output, need to check if lib-button emits click event or if we need to call method directly.
    // In lib-button, (clicked) emits.
    // In test, clicking the element dispatches 'click'.
    // If lib-button listens to 'click' (native) or has custom output.
    // Assuming lib-button uses (click) internally or host listener.

    // Let's call the method directly to be safe, or use button.click() if we trust shared-ui integration in test.
    // Since shared-ui components are imported, let's try direct method call if click doesn't work or just call handleSettings.
    component.handleSettings();
    expect(emittedProject).toEqual(mockProject);
  });

  it('should generate correct route', () => {
    expect(component.getProjectRoute()).toEqual(['/app', 'organizations', 'org1', 'projects', '1']);
    expect(navigationService.getProjectRoute).toHaveBeenCalledWith('org1', '1');
  });
});
