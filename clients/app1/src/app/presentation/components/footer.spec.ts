import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Footer } from './footer';
import { RouterTestingModule } from '@angular/router/testing';
import { Icon } from 'shared-ui';

describe('Footer', () => {
  let component: Footer;
  let fixture: ComponentFixture<Footer>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Footer, Icon, RouterTestingModule],
    }).compileComponents();

    fixture = TestBed.createComponent(Footer);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display brand', () => {
    const brand = fixture.nativeElement.querySelector('.footer_brand');
    expect(brand).toBeTruthy();
  });

  it('should display product links', () => {
    const productSection = fixture.nativeElement.querySelector('.footer_section');
    expect(productSection).toBeTruthy();
    expect(component.productLinks.length).toBeGreaterThan(0);
  });

  it('should display legal links', () => {
    expect(component.legalLinks.length).toBeGreaterThan(0);
  });

  it('should display social links', () => {
    const socialLinks = fixture.nativeElement.querySelectorAll('.footer_social-link');
    expect(socialLinks.length).toBe(component.socialLinks.length);
  });

  it('should display copyright with current year', () => {
    const copyright = fixture.nativeElement.querySelector('.footer_copyright-text');
    expect(copyright).toBeTruthy();
    expect(copyright.textContent).toContain(component.currentYear.toString());
  });

  it('should have contact email', () => {
    const emailLink = fixture.nativeElement.querySelector('a[href^="mailto:"]');
    expect(emailLink).toBeTruthy();
  });
});
