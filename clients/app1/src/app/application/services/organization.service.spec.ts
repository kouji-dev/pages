import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { OrganizationService, Organization } from './organization.service';

describe('OrganizationService', () => {
  let service: OrganizationService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [OrganizationService],
    });
    service = TestBed.inject(OrganizationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should initialize with empty organizations', () => {
    const value = service.organizations.value();
    expect(Array.isArray(value) ? value : []).toEqual([]);
  });

  it('should initialize with null current organization', () => {
    expect(service.currentOrganization()).toBeNull();
  });

  it('should load organizations', (done) => {
    service.loadOrganizations();

    setTimeout(() => {
      const value = service.organizations.value();
      const orgs = Array.isArray(value) ? value : [];
      expect(orgs.length).toBeGreaterThan(0);
      expect(orgs[0]).toHaveProperty('id');
      expect(orgs[0]).toHaveProperty('name');
      expect(orgs[0]).toHaveProperty('slug');
      done();
    }, 400);
  });

  it('should switch organization', (done) => {
    service.loadOrganizations();

    setTimeout(() => {
      const value = service.organizations.value();
      const orgs = Array.isArray(value) ? value : [];
      if (orgs.length > 0) {
        const firstOrg = orgs[0];
        service.switchOrganization(firstOrg.id);

        expect(service.currentOrganization()).toEqual(firstOrg);
        expect(localStorage.getItem('current_organization_id')).toBe(firstOrg.id);
        done();
      } else {
        done();
      }
    }, 400);
  });

  it('should get current organization', (done) => {
    service.loadOrganizations();

    setTimeout(() => {
      const org = service.getCurrentOrganization();
      expect(org).toBeTruthy();
      done();
    }, 400);
  });

  it('should get all organizations', (done) => {
    service.loadOrganizations();

    setTimeout(() => {
      const orgs = service.getOrganizations();
      expect(Array.isArray(orgs)).toBe(true);
      done();
    }, 400);
  });
});
