import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HeroSection } from './hero-section';
import { RouterTestingModule } from '@angular/router/testing';
import { Button, Icon } from 'shared-ui';

describe('HeroSection', () => {
  let component: HeroSection;
  let fixture: ComponentFixture<HeroSection>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeroSection, Button, Icon, RouterTestingModule],
    }).compileComponents();

    fixture = TestBed.createComponent(HeroSection);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display headline', () => {
    const headline = fixture.nativeElement.querySelector('.hero-section_headline');
    expect(headline).toBeTruthy();
    expect(headline.textContent).toContain('Build Better Together');
  });

  it('should display subheading', () => {
    const subheading = fixture.nativeElement.querySelector('.hero-section_subheading');
    expect(subheading).toBeTruthy();
    expect(subheading.textContent).toContain('Collaborate, Create, Succeed');
  });

  it('should display value proposition', () => {
    const description = fixture.nativeElement.querySelector('.hero-section_description');
    expect(description).toBeTruthy();
    expect(description.textContent).toContain('Pages is your all-in-one workspace');
  });

  it('should display primary CTA button', () => {
    const buttons = fixture.nativeElement.querySelectorAll('lib-button');
    expect(buttons.length).toBeGreaterThanOrEqual(1);
    const primaryButton = Array.from(buttons).find((btn: any) =>
      btn.textContent.trim().includes('Get Started'),
    );
    expect(primaryButton).toBeTruthy();
  });

  it('should display secondary CTA button', () => {
    const buttons = fixture.nativeElement.querySelectorAll('lib-button');
    expect(buttons.length).toBeGreaterThanOrEqual(2);
    const secondaryButton = Array.from(buttons).find((btn: any) =>
      btn.textContent.trim().includes('Learn More'),
    );
    expect(secondaryButton).toBeTruthy();
  });

  it('should have responsive container classes', () => {
    const container = fixture.nativeElement.querySelector('.hero-section_container');
    expect(container).toHaveClass('grid');
    expect(container).toHaveClass('grid-cols-1');
    expect(container).toHaveClass('lg:grid-cols-2');
  });

  it('should have hero image placeholder', () => {
    const imagePlaceholder = fixture.nativeElement.querySelector('.hero-section_image-placeholder');
    expect(imagePlaceholder).toBeTruthy();
  });
});
