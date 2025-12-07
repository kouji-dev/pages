import { HttpInterceptorFn, HttpRequest, HttpResponse } from '@angular/common/http';
import { of, delay } from 'rxjs';

interface CreateOrganizationRequest {
  name: string;
  slug: string;
  description?: string;
}

interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  memberCount?: number;
}

/**
 * Mock data storage keys
 */
const STORAGE_KEYS = {
  ORGANIZATIONS: 'mock_organizations',
} as const;

/**
 * Default mock data (used when localStorage is empty)
 */
const DEFAULT_MOCK_DATA: { organizations: Organization[] } = {
  organizations: [
    {
      id: 'org-1',
      name: 'Acme Corp',
      slug: 'acme-corp',
      description: 'Main organization',
      memberCount: 5,
    },
    {
      id: 'org-2',
      name: 'Personal',
      slug: 'personal',
      description: 'Personal workspace',
      memberCount: 1,
    },
  ],
};

/**
 * Helper to get data from localStorage or use default
 */
function getFromStorage<T>(key: string, defaultValue: T): T {
  try {
    const stored = localStorage.getItem(key);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.warn(`Failed to load from localStorage key "${key}":`, error);
  }
  return defaultValue;
}

/**
 * Helper to save data to localStorage
 */
function saveToStorage<T>(key: string, data: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (error) {
    console.warn(`Failed to save to localStorage key "${key}":`, error);
  }
}

/**
 * Mock API Interceptor
 * Intercepts HTTP requests and returns mock data from localStorage or defaults
 *
 * TODO: Remove this interceptor when backend API is ready
 * When backend is ready, remove this interceptor from app.config.ts providers
 */
export const mockApiInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next) => {
  const url = req.url;
  const method = req.method;

  // Only intercept API requests (not static assets, etc.)
  if (!url.includes('/api/')) {
    return next(req);
  }

  // Mock organizations API
  if (url.includes('/api/organizations')) {
    // GET /api/organizations - List organizations
    if (method === 'GET' && !url.match(/\/api\/organizations\/[^/]+/)) {
      const organizations = getFromStorage(
        STORAGE_KEYS.ORGANIZATIONS,
        DEFAULT_MOCK_DATA.organizations,
      );
      return of(new HttpResponse({ status: 200, body: organizations })).pipe(delay(300));
    }

    // GET /api/organizations/:id - Get organization by ID
    if (method === 'GET') {
      const match = url.match(/\/api\/organizations\/([^/]+)/);
      if (match) {
        const id = match[1];
        const organizations = getFromStorage(
          STORAGE_KEYS.ORGANIZATIONS,
          DEFAULT_MOCK_DATA.organizations,
        );
        const org = organizations.find((o) => o.id === id);
        if (org) {
          return of(new HttpResponse({ status: 200, body: org })).pipe(delay(200));
        }
        return of(
          new HttpResponse({ status: 404, body: { error: 'Organization not found' } }),
        ).pipe(delay(200));
      }
    }

    // POST /api/organizations - Create organization
    if (method === 'POST') {
      const organizations = getFromStorage(
        STORAGE_KEYS.ORGANIZATIONS,
        DEFAULT_MOCK_DATA.organizations,
      );
      const body = req.body as CreateOrganizationRequest;
      const newOrg = {
        id: `org-${Date.now()}`,
        ...(body || {}),
        memberCount: 1,
      };
      const updatedOrgs = [...organizations, newOrg];
      saveToStorage(STORAGE_KEYS.ORGANIZATIONS, updatedOrgs);
      return of(new HttpResponse({ status: 201, body: newOrg })).pipe(delay(500));
    }

    // PUT/PATCH /api/organizations/:id - Update organization
    if (method === 'PUT' || method === 'PATCH') {
      const match = url.match(/\/api\/organizations\/([^/]+)/);
      if (match) {
        const id = match[1];
        const organizations = getFromStorage(
          STORAGE_KEYS.ORGANIZATIONS,
          DEFAULT_MOCK_DATA.organizations,
        );
        const index = organizations.findIndex((o) => o.id === id);
        if (index !== -1) {
          const body = req.body as Partial<Organization>;
          const updatedOrg = { ...organizations[index], ...(body || {}) };
          const updatedOrgs = [...organizations];
          updatedOrgs[index] = updatedOrg;
          saveToStorage(STORAGE_KEYS.ORGANIZATIONS, updatedOrgs);
          return of(new HttpResponse({ status: 200, body: updatedOrg })).pipe(delay(300));
        }
        return of(
          new HttpResponse({ status: 404, body: { error: 'Organization not found' } }),
        ).pipe(delay(200));
      }
    }

    // DELETE /api/organizations/:id - Delete organization
    if (method === 'DELETE') {
      const match = url.match(/\/api\/organizations\/([^/]+)/);
      if (match) {
        const id = match[1];
        const organizations = getFromStorage(
          STORAGE_KEYS.ORGANIZATIONS,
          DEFAULT_MOCK_DATA.organizations,
        );
        const filteredOrgs = organizations.filter((o) => o.id !== id);
        if (filteredOrgs.length !== organizations.length) {
          saveToStorage(STORAGE_KEYS.ORGANIZATIONS, filteredOrgs);
          return of(new HttpResponse({ status: 204 })).pipe(delay(300));
        }
        return of(
          new HttpResponse({ status: 404, body: { error: 'Organization not found' } }),
        ).pipe(delay(200));
      }
    }
  }

  // For any other API requests, pass through (or return 404)
  // When backend is ready, remove this interceptor so requests go through normally
  console.warn(`Unmocked API request: ${method} ${url}`);
  return next(req);
};
