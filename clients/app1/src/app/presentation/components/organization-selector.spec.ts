import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { OrganizationSelector } from './organization-selector';
import { OrganizationService } from '../../application/services/organization.service';
import { Icon, Dropdown } from 'shared-ui';
import { Router } from '@angular/router';

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
    await TestBed.configureTestingModule({
      imports: [OrganizationSelector, Icon, Dropdown, TestHostComponent],
      providers: [
        OrganizationService,
        {
          provide: Router,
          useValue: {
            navigate: jasmine.createSpy('navigate'),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    organizationService = TestBed.inject(OrganizationService);
    router = TestBed.inject(Router);
    const selectorElement = fixture.nativeElement.querySelector('app-organization-selector');
    component = fixture.debugElement.children[0].componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display current organization name', (done) => {
    organizationService.loadOrganizations();

    setTimeout(() => {
      fixture.detectChanges();
      const trigger = fixture.nativeElement.querySelector('.org-selector_trigger');
      expect(trigger).toBeTruthy();
      const nameElement = fixture.nativeElement.querySelector('.org-selector_current-name');
      expect(nameElement?.textContent).toBeTruthy();
      done();
    }, 400);
  });

  it('should open dropdown when trigger is clicked', (done) => {
    organizationService.loadOrganizations();

    setTimeout(() => {
      fixture.detectChanges();
      const trigger = fixture.nativeElement.querySelector('.org-selector_trigger');
      trigger.click();
      fixture.detectChanges();

      const dropdown = fixture.nativeElement.querySelector('.org-selector_dropdown');
      expect(dropdown).toBeTruthy();
      done();
    }, 400);
  });

  it('should display list of organizations in dropdown', (done) => {
    organizationService.loadOrganizations();

    setTimeout(() => {
      fixture.detectChanges();
      const trigger = fixture.nativeElement.querySelector('.org-selector_trigger');
      trigger.click();
      fixture.detectChanges();

      const items = fixture.nativeElement.querySelectorAll('.org-selector_item');
      expect(items.length).toBeGreaterThan(0);
      done();
    }, 400);
  });

  it('should mark current organization as active', (done) => {
    organizationService.loadOrganizations();

    setTimeout(() => {
      fixture.detectChanges();
      const trigger = fixture.nativeElement.querySelector('.org-selector_trigger');
      trigger.click();
      fixture.detectChanges();

      const activeItem = fixture.nativeElement.querySelector('.org-selector_item--active');
      expect(activeItem).toBeTruthy();
      done();
    }, 400);
  });
});
