import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChangeProjectMemberRoleModal } from './change-project-member-role-modal';
import { ProjectMembersService } from '../../../../application/services/project-members.service';
import { Modal, ToastService } from 'shared-ui';
import { TranslateModule } from '@ngx-translate/core';

describe('ChangeProjectMemberRoleModal', () => {
  let component: ChangeProjectMemberRoleModal;
  let fixture: ComponentFixture<ChangeProjectMemberRoleModal>;
  let membersService: any;
  let modal: any;
  let toast: any;

  const mockMember = {
    user_id: '1',
    user_name: 'User 1',
    user_email: 'user1@example.com',
    role: 'member' as const,
    joined_at: '2024-01-01',
  };

  beforeEach(async () => {
    membersService = {
      updateMemberRole: vi.fn(),
    };

    modal = {
      close: vi.fn(),
    };

    toast = {
      success: vi.fn(),
      error: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [ChangeProjectMemberRoleModal, TranslateModule.forRoot()],
      providers: [
        { provide: ProjectMembersService, useValue: membersService },
        { provide: Modal, useValue: modal },
        { provide: ToastService, useValue: toast },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ChangeProjectMemberRoleModal);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('projectId', '1');
    fixture.componentRef.setInput('member', mockMember);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should update role', async () => {
    component.selectRole('admin');
    await component.handleSubmit();
    expect(membersService.updateMemberRole).toHaveBeenCalledWith('1', '1', { role: 'admin' });
    expect(toast.success).toHaveBeenCalled();
    expect(modal.close).toHaveBeenCalled();
  });
});
