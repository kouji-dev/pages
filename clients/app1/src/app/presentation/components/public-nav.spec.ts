import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PublicNav } from './public-nav';
import { RouterTestingModule } from '@angular/router/testing';
import { Button, Icon } from 'shared-ui';

describe('PublicNav', () => {
  let component: PublicNav;
  let fixture: ComponentFixture<PublicNav>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PublicNav, Button, Icon, RouterTestingModule],
    }).compileComponents();

    fixture = TestBed.createComponent(PublicNav);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display logo', () => {
    const logo = fixture.nativeElement.querySelector('.public-nav_logo');
    expect(logo).toBeTruthy();
  });

  it('should display desktop navigation links', () => {
    const links = fixture.nativeElement.querySelectorAll('.public-nav_link');
    expect(links.length).toBeGreaterThanOrEqual(3);
  });

  it('should display Sign Up and Log In buttons', () => {
    const buttons = fixture.nativeElement.querySelectorAll('lib-button');
    expect(buttons.length).toBeGreaterThanOrEqual(2);
  });

  it('should toggle mobile menu when button is clicked', () => {
    const toggleButton = fixture.nativeElement.querySelector('.public-nav_mobile-toggle');
    expect(component.isMobileMenuOpen()).toBeFalse();

    toggleButton?.click();
    fixture.detectChanges();

    expect(component.isMobileMenuOpen()).toBeTrue();
  });

  it('should show mobile menu when toggled', () => {
    component.toggleMobileMenu();
    fixture.detectChanges();

    const mobileMenu = fixture.nativeElement.querySelector('.public-nav_mobile');
    expect(mobileMenu).toBeTruthy();
  });
});
