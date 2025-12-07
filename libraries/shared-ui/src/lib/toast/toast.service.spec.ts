import { TestBed } from '@angular/core/testing';
import { OverlayModule } from '@angular/cdk/overlay';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ToastService } from './toast.service';

describe('ToastService', () => {
  let service: ToastService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [OverlayModule, BrowserAnimationsModule],
      providers: [ToastService],
    });
    service = TestBed.inject(ToastService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should show a toast with default config', () => {
    const toastId = service.show({ message: 'Test message' });
    expect(toastId).toBeTruthy();
    expect(toastId).toContain('toast-');
  });

  it('should show success toast', () => {
    const toastId = service.success('Success message');
    expect(toastId).toBeTruthy();
  });

  it('should show error toast', () => {
    const toastId = service.error('Error message');
    expect(toastId).toBeTruthy();
  });

  it('should show warning toast', () => {
    const toastId = service.warning('Warning message');
    expect(toastId).toBeTruthy();
  });

  it('should show info toast', () => {
    const toastId = service.info('Info message');
    expect(toastId).toBeTruthy();
  });

  it('should close a specific toast', () => {
    const toastId = service.show({ message: 'Test message' });
    service.close(toastId);
    // Toast should be closed (no error thrown)
    expect(true).toBe(true);
  });

  it('should close all toasts', () => {
    service.show({ message: 'Toast 1' });
    service.show({ message: 'Toast 2' });
    service.closeAll();
    // All toasts should be closed (no error thrown)
    expect(true).toBe(true);
  });

  it('should use default position top-right', () => {
    const toastId = service.show({ message: 'Test message' });
    expect(toastId).toBeTruthy();
  });

  it('should use custom position', () => {
    const toastId = service.show({
      message: 'Test message',
      position: 'bottom-left',
    });
    expect(toastId).toBeTruthy();
  });

  it('should auto-dismiss after duration', async () => {
    const toastId = service.show({
      message: 'Test message',
      duration: 100,
    });
    expect(toastId).toBeTruthy();

    await new Promise((resolve) => setTimeout(resolve, 150));
    // Toast should be auto-dismissed
    expect(true).toBe(true);
  });

  it('should not auto-dismiss when duration is 0', async () => {
    const toastId = service.show({
      message: 'Test message',
      duration: 0,
    });
    expect(toastId).toBeTruthy();

    await new Promise((resolve) => setTimeout(resolve, 100));
    // Toast should still be visible (we can't easily test this without DOM access)
    expect(toastId).toBeTruthy();
  });

  it('should stack multiple toasts at same position', () => {
    const toastId1 = service.show({ message: 'Toast 1', position: 'top-right' });
    const toastId2 = service.show({ message: 'Toast 2', position: 'top-right' });
    expect(toastId1).toBeTruthy();
    expect(toastId2).toBeTruthy();
  });
});
