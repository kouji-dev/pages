import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProjectMemberList } from './project-member-list';
import { ProjectMembersService } from '../../../../application/services/project-members.service';
import { AuthService } from '../../../../core/auth/auth.service';
import { Modal, ToastService } from 'shared-ui';
import { TranslateModule } from '@ngx-translate/core';
import { signal } from '@angular/core';

describe('ProjectMemberList', () => {
  let component: ProjectMemberList;
  let fixture: ComponentFixture<ProjectMemberList>;
  let membersService: any;
  let authService: any;
  let modal: any;
  let toast: any;

  const mockMembers = [
    { user_id: '1', user_name: 'User 1', user_email: 'user1@example.com', role: 'admin' },
    { user_id: '2', user_name: 'User 2', user_email: 'user2@example.com', role: 'member' },
  ];

  beforeEach(async () => {
    membersService = {
      members: signal(mockMembers),
      isLoading: signal(false),
      hasError: signal(false),
      error: signal(null),
      addMember: vi.fn(),
      updateMemberRole: vi.fn(),
      removeMember: vi.fn(),
      reloadMembers: vi.fn(),
    };

    authService = {
      getUser: vi.fn().mockReturnValue({ id: '1', name: 'User 1' }),
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
      imports: [ProjectMemberList, TranslateModule.forRoot()],
      providers: [
        { provide: ProjectMembersService, useValue: membersService },
        { provide: AuthService, useValue: authService },
        { provide: Modal, useValue: modal },
        { provide: ToastService, useValue: toast },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProjectMemberList);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('projectId', '1');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display members', () => {
    expect(component.members().length).toBe(2);
  });

  it('should open add member modal', () => {
    component.handleAddMember();
    expect(modal.open).toHaveBeenCalled();
  });
});
