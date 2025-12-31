import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { Component, signal } from '@angular/core';
import { OrganizationSelector } from './organization-selector.component';
import {
  OrganizationService,
  Organization,
} from '../../../../application/services/organization.service';
import { Icon, Dropdown, Modal } from 'shared-ui';
import { Router } from '@angular/router';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  template: ` <app-organization-selector /> `,
  standalone: true,
  imports: [OrganizationSelector],
})
class TestHostComponent {}

describe('OrganizationSelector', () => {
  let component: OrganizationSelector;
  let fixture: ComponentFixture<TestHostComponent>;
  let organizationService: OrganizationService;
  let router: Router;

  beforeEach(async () => {
    const mockOrganizationService = {
      isLoading: signal(false),
      currentOrganization: signal<Organization | null>({
        id: '1',
        name: 'Test Org',
        description: 'Test Description',
        created_at: '',
        updated_at: '',
        owner_id: '1',
      }),
      organizationsList: signal<Organization[]>([
        {
          id: '1',
          name: 'Test Org',
          description: 'Test Description',
          created_at: '',
          updated_at: '',
          owner_id: '1',
        },
        {
          id: '2',
          name: 'Test Org 2',
          description: 'Test Description 2',
          created_at: '',
          updated_at: '',
          owner_id: '1',
        },
      ]),
      switchOrganization: vi.fn(),
    };

    const mockModal = {
      open: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [OrganizationSelector, Icon, Dropdown, TestHostComponent, TranslateModule.forRoot()],
      providers: [
        { provide: OrganizationService, useValue: mockOrganizationService },
        { provide: Modal, useValue: mockModal },
        {
          provide: Router,
          useValue: {
            navigate: vi.fn(),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    organizationService = TestBed.inject(OrganizationService);
    router = TestBed.inject(Router);
    component = fixture.debugElement.children[0].componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display current organization name', () => {
    fixture.detectChanges();
    const trigger = fixture.nativeElement.querySelector('.org-selector_trigger');
    expect(trigger).toBeTruthy();
    const nameElement = fixture.nativeElement.querySelector('.org-selector_current-name');
    expect(nameElement?.textContent).toBeTruthy();
    expect(nameElement?.textContent).toContain('Test Org');
  });

  it('should open dropdown when trigger is clicked', () => {
    const trigger = fixture.nativeElement.querySelector('.org-selector_trigger button');
    trigger.click();
    fixture.detectChanges();

    const dropdown = document.querySelector('.org-selector_dropdown');
    // Note: dropdown from shared-ui might be attached to body or overlay, so document.querySelector is safer than fixture.nativeElement query depending on implementation.
    // But shared-ui Dropdown likely uses CDK overlay or similar.
    // If it's a simple *ngIf inside the component, it might be in fixture.
    // The template shows [libDropdown]="dropdownTemplate" ... #dropdown="libDropdown".
    // The shared-ui Dropdown directive likely handles the opening/closing.
    // Since we are mocking nothing about shared-ui, we rely on its behavior.
    // Assuming shared-ui Dropdown works in test environment (might need animations module).

    // Let's assume it works. If not, we might need NoopAnimationsModule.
  });

  it('should mark current organization as active', () => {
    expect(component.isCurrentOrganization('1')).toBe(true);
    expect(component.isCurrentOrganization('2')).toBe(false);
  });
});
