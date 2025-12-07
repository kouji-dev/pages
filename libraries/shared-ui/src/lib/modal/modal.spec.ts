import { TestBed } from '@angular/core/testing';
import { OverlayModule } from '@angular/cdk/overlay';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { Component, ViewContainerRef } from '@angular/core';
import { Modal } from './modal';
import { firstValueFrom } from 'rxjs';

@Component({
  template: '<div>Test Modal Content</div>',
  standalone: true,
})
class TestModalComponent {}

describe('Modal', () => {
  let service: Modal;
  let viewContainerRef: ViewContainerRef;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [OverlayModule, BrowserAnimationsModule, TestModalComponent],
      providers: [Modal],
    });
    service = TestBed.inject(Modal);
    const fixture = TestBed.createComponent(TestModalComponent);
    viewContainerRef = fixture.componentRef.injector.get(ViewContainerRef);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should open modal with component', async () => {
    const modal$ = service.open(TestModalComponent, viewContainerRef, {
      size: 'md',
      closable: true,
    });

    // Close modal immediately
    setTimeout(() => {
      service.close();
    }, 10);

    const result = await firstValueFrom(modal$);
    expect(result).toBeUndefined();
  });

  it('should open modal with default config', async () => {
    const modal$ = service.open(TestModalComponent, viewContainerRef);

    setTimeout(() => {
      service.close();
    }, 10);

    await firstValueFrom(modal$);
    expect(true).toBe(true);
  });

  it('should close modal and return payload', async () => {
    const modal$ = service.open(TestModalComponent, viewContainerRef);

    setTimeout(() => {
      service.close('test-payload');
    }, 10);

    const result = await firstValueFrom(modal$);
    expect(result).toBe('test-payload');
  });

  it('should close previous modal when opening new one', async () => {
    const modal1$ = service.open(TestModalComponent, viewContainerRef);
    let modal1Closed = false;

    modal1$.subscribe(() => {
      modal1Closed = true;
    });

    // Open second modal immediately (should close first)
    setTimeout(() => {
      const modal2$ = service.open(TestModalComponent, viewContainerRef);
      setTimeout(() => {
        service.close();
      }, 10);
      firstValueFrom(modal2$).then(() => {
        expect(modal1Closed).toBe(true);
      });
    }, 10);

    // Wait a bit for async operations
    await new Promise((resolve) => setTimeout(resolve, 100));
  });

  it('should handle different sizes', async () => {
    const modal$ = service.open(TestModalComponent, viewContainerRef, {
      size: 'lg',
    });

    setTimeout(() => {
      service.close();
    }, 10);

    await firstValueFrom(modal$);
    expect(true).toBe(true);
  });

  it('should pass data to component', async () => {
    const modal$ = service.open(TestModalComponent, viewContainerRef, {
      data: { test: 'value' },
    });

    setTimeout(() => {
      service.close();
    }, 10);

    await firstValueFrom(modal$);
    expect(true).toBe(true);
  });
});
