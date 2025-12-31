import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MemberList } from './member-list.component';
import { OrganizationMember } from '../../../../application/services/organization-members.service';
import { Button, Icon, Dropdown, LoadingState, ErrorState, EmptyState, Table } from 'shared-ui';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('MemberList', () => {
  let component: MemberList;
  let fixture: ComponentFixture<MemberList>;
  let element: HTMLElement;

  const mockMembers: OrganizationMember[] = [
    {
      user_id: 'user1',
      user_name: 'Test User 1',
      user_email: 'user1@test.com',
      role: 'admin',
      avatar_url: null,
      organization_id: 'org1',
      joined_at: new Date().toISOString(),
    },
    {
      user_id: 'user2',
      user_name: 'Test User 2',
      user_email: 'user2@test.com',
      role: 'member',
      avatar_url: null,
      organization_id: 'org1',
      joined_at: new Date().toISOString(),
    },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MemberList, Button, Icon, Dropdown, LoadingState, ErrorState, EmptyState, Table],
    }).compileComponents();

    fixture = TestBed.createComponent(MemberList);
    component = fixture.componentInstance;
    element = fixture.nativeElement;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display title and subtitle', () => {
    fixture.componentRef.setInput('members', mockMembers);
    fixture.componentRef.setInput('isLoading', false);
    fixture.componentRef.setInput('hasError', false);
    fixture.detectChanges();
    const title = element.querySelector('.member-list_title');
    const subtitle = element.querySelector('.member-list_subtitle');
    expect(title?.textContent?.trim()).toBe('members.title');
    expect(subtitle?.textContent?.trim()).toContain('members.subtitle');
  });

  it('should display add member button when canAddMembers is true', () => {
    fixture.componentRef.setInput('members', mockMembers);
    fixture.componentRef.setInput('isLoading', false);
    fixture.componentRef.setInput('hasError', false);
    fixture.componentRef.setInput('canAddMembers', true);
    fixture.detectChanges();
    const addButton = element.querySelector('lib-button[leftIcon="plus"]');
    expect(addButton).toBeTruthy();
  });

  it('should not display add member button when canAddMembers is false', () => {
    fixture.componentRef.setInput('members', mockMembers);
    fixture.componentRef.setInput('isLoading', false);
    fixture.componentRef.setInput('hasError', false);
    fixture.componentRef.setInput('canAddMembers', false);
    fixture.detectChanges();
    const addButton = element.querySelector('lib-button[leftIcon="plus"]');
    expect(addButton).toBeFalsy();
  });

  it('should display loading state when loading', () => {
    fixture.componentRef.setInput('members', []);
    fixture.componentRef.setInput('isLoading', true);
    fixture.componentRef.setInput('hasError', false);
    fixture.detectChanges();
    const loadingState = element.querySelector('lib-loading-state');
    expect(loadingState).toBeTruthy();
  });

  it('should display error state when there is an error', () => {
    fixture.componentRef.setInput('members', []);
    fixture.componentRef.setInput('isLoading', false);
    fixture.componentRef.setInput('hasError', true);
    fixture.componentRef.setInput('errorMessage', 'Test error');
    fixture.detectChanges();
    const errorState = element.querySelector('lib-error-state');
    expect(errorState).toBeTruthy();
  });

  it('should display empty state when no members', () => {
    fixture.componentRef.setInput('members', []);
    fixture.componentRef.setInput('isLoading', false);
    fixture.componentRef.setInput('hasError', false);
    fixture.detectChanges();
    const emptyState = element.querySelector('lib-empty-state');
    expect(emptyState).toBeTruthy();
  });

  it('should display table when members exist', () => {
    fixture.componentRef.setInput('members', mockMembers);
    fixture.componentRef.setInput('isLoading', false);
    fixture.componentRef.setInput('hasError', false);
    fixture.detectChanges();
    const table = element.querySelector('lib-table');
    expect(table).toBeTruthy();
  });

  it('should emit onAddMember when add member button is clicked', () => {
    let addMemberEmitted = false;
    component.onAddMember.subscribe(() => {
      addMemberEmitted = true;
    });
    fixture.componentRef.setInput('members', mockMembers);
    fixture.componentRef.setInput('isLoading', false);
    fixture.componentRef.setInput('hasError', false);
    fixture.componentRef.setInput('canAddMembers', true);
    fixture.detectChanges();
    component.handleAddMember();
    expect(addMemberEmitted).toBe(true);
  });

  it('should emit onRetry when retry is clicked', () => {
    let retryEmitted = false;
    component.onRetry.subscribe(() => {
      retryEmitted = true;
    });
    component.handleRetry();
    expect(retryEmitted).toBe(true);
  });

  it('should compute columns correctly', () => {
    fixture.detectChanges();
    const columns = component.columns();
    expect(columns.length).toBe(2);
    expect(columns[0].key).toBe('member');
    expect(columns[1].key).toBe('role');
  });

  it('should get initials from name', () => {
    expect(component.getInitials('John Doe')).toBe('JD');
    expect(component.getInitials('John')).toBe('J');
    expect(component.getInitials('John Michael Smith')).toBe('JM');
    expect(component.getInitials('')).toBe('U');
  });

  it('should get role label correctly', () => {
    expect(component.getRoleLabel('admin')).toBe('members.admin');
    expect(component.getRoleLabel('member')).toBe('members.member');
    expect(component.getRoleLabel('viewer')).toBe('members.viewer');
  });

  it('should allow admin to manage members', () => {
    fixture.componentRef.setInput('currentUserRole', 'admin');
    fixture.detectChanges();
    expect(component.canManageMember(mockMembers[0])).toBe(true);
  });

  it('should not allow non-admin to manage members', () => {
    fixture.componentRef.setInput('currentUserRole', 'member');
    fixture.detectChanges();
    expect(component.canManageMember(mockMembers[0])).toBe(false);
  });

  it('should allow admin to change role of other members', () => {
    fixture.componentRef.setInput('currentUserRole', 'admin');
    fixture.componentRef.setInput('currentUserId', 'user1');
    fixture.detectChanges();
    expect(component.canChangeRole(mockMembers[1])).toBe(true);
  });

  it('should not allow admin to change their own role', () => {
    fixture.componentRef.setInput('currentUserRole', 'admin');
    fixture.componentRef.setInput('currentUserId', 'user1');
    fixture.detectChanges();
    expect(component.canChangeRole(mockMembers[0])).toBe(false);
  });

  it('should allow admin to remove members', () => {
    fixture.componentRef.setInput('currentUserRole', 'admin');
    fixture.detectChanges();
    expect(component.canRemoveMember(mockMembers[1])).toBe(true);
  });

  it('should allow user to remove themselves', () => {
    fixture.componentRef.setInput('currentUserRole', 'member');
    fixture.componentRef.setInput('currentUserId', 'user2');
    fixture.detectChanges();
    expect(component.canRemoveMember(mockMembers[1])).toBe(true);
  });

  it('should emit onChangeRole when change role is clicked', () => {
    let changeRoleEmitted = false;
    let emittedMember: OrganizationMember | null = null;
    component.onChangeRole.subscribe((member) => {
      changeRoleEmitted = true;
      emittedMember = member;
    });
    const mockDropdown = { open: { set: () => {} } } as any;
    component.handleChangeRole(mockMembers[0], mockDropdown);
    expect(changeRoleEmitted).toBe(true);
    expect(emittedMember).toBe(mockMembers[0]);
  });

  it('should emit onRemoveMember when remove member is clicked', () => {
    let removeMemberEmitted = false;
    let emittedMember: OrganizationMember | null = null;
    component.onRemoveMember.subscribe((member) => {
      removeMemberEmitted = true;
      emittedMember = member;
    });
    const mockDropdown = { open: { set: () => {} } } as any;
    component.handleRemoveMember(mockMembers[0], mockDropdown);
    expect(removeMemberEmitted).toBe(true);
    expect(emittedMember).toBe(mockMembers[0]);
  });

  it('should track members by user_id', () => {
    expect(component.trackByMemberId(mockMembers[0])).toBe('user1');
    expect(component.trackByMemberId(mockMembers[1])).toBe('user2');
  });

  it('should compute hasManageableMembers correctly', () => {
    fixture.componentRef.setInput('members', mockMembers);
    fixture.componentRef.setInput('currentUserRole', 'admin');
    fixture.detectChanges();
    expect(component.hasManageableMembers()).toBe(true);
  });

  it('should compute hasManageableMembers as false when no manageable members', () => {
    fixture.componentRef.setInput('members', mockMembers);
    fixture.componentRef.setInput('currentUserRole', 'member');
    fixture.detectChanges();
    expect(component.hasManageableMembers()).toBe(false);
  });
});
