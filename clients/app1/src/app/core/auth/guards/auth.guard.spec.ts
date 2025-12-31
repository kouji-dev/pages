import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { authGuard } from './auth.guard';
import { AuthService } from '../auth.service';
import { vi, describe, it, expect, beforeEach, Mock } from 'vitest';

describe('authGuard', () => {
  let authService: { isAuthenticated: Mock; initialized: Promise<void>; hasAccessToken: Mock };
  let router: { navigate: Mock };

  beforeEach(() => {
    authService = {
      isAuthenticated: vi.fn(),
      initialized: Promise.resolve(),
      hasAccessToken: vi.fn(),
    };
    router = {
      navigate: vi.fn(),
    };

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: router },
      ],
    });
  });

  it('should allow access when user is authenticated', async () => {
    // Arrange
    authService.isAuthenticated.mockReturnValue(true);
    authService.hasAccessToken.mockReturnValue(true);

    // Act
    const result = await TestBed.runInInjectionContext(() => authGuard({} as any, {} as any));

    // Assert
    expect(result).toBe(true);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('should redirect to login when user is not authenticated', async () => {
    // Arrange
    authService.isAuthenticated.mockReturnValue(false);

    // Act
    const result = await TestBed.runInInjectionContext(() => authGuard({} as any, {} as any));

    // Assert
    expect(result).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });
});
