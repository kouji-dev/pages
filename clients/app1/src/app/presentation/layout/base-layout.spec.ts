import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { BaseLayout } from './base-layout';

describe('BaseLayout', () => {
  let component: BaseLayout;
  let fixture: ComponentFixture<BaseLayout>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BaseLayout, RouterTestingModule],
    }).compileComponents();

    fixture = TestBed.createComponent(BaseLayout);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have sidebar closed by default', () => {
    expect(component.sidebarOpen()).toBe(false);
  });

  it('should toggle sidebar when toggleSidebar is called', () => {
    expect(component.sidebarOpen()).toBe(false);
    component.toggleSidebar();
    expect(component.sidebarOpen()).toBe(true);
    component.toggleSidebar();
    expect(component.sidebarOpen()).toBe(false);
  });

  it('should close sidebar when closeSidebar is called', () => {
    component.toggleSidebar();
    expect(component.sidebarOpen()).toBe(true);
    component.closeSidebar();
    expect(component.sidebarOpen()).toBe(false);
  });

  it('should show footer by default', () => {
    expect(component.showFooter()).toBe(true);
  });

  it('should show nav by default', () => {
    expect(component.showNav()).toBe(true);
  });

  it('should display current year in footer', () => {
    const currentYear = new Date().getFullYear();
    expect(component.currentYear()).toBe(currentYear);
  });

  it('should render header with logo', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const logo = compiled.querySelector('.layout_logo-text');
    expect(logo?.textContent).toContain('Pages');
  });

  it('should render main content area with router outlet', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const main = compiled.querySelector('.layout_main');
    expect(main).toBeTruthy();
    const routerOutlet = compiled.querySelector('router-outlet');
    expect(routerOutlet).toBeTruthy();
  });
});
