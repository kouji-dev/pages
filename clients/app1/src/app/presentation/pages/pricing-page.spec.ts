import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PricingPage } from './pricing-page';
import { Button, Icon } from 'shared-ui';

describe('PricingPage', () => {
  let component: PricingPage;
  let fixture: ComponentFixture<PricingPage>;
  let element: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PricingPage, Button, Icon],
    }).compileComponents();

    fixture = TestBed.createComponent(PricingPage);
    component = fixture.componentInstance;
    element = fixture.nativeElement;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render page title', () => {
    const title = element.querySelector('.pricing-page_title');
    expect(title).toBeTruthy();
    expect(title?.textContent).toContain('Simple, Transparent Pricing');
  });

  it('should render all pricing tiers', () => {
    const tiers = element.querySelectorAll('.pricing-page_tier');
    expect(tiers.length).toBe(5); // Free, Starter, Professional, Business, Enterprise
  });

  it('should mark popular tier', () => {
    const popularTier = element.querySelector('.pricing-page_tier--popular');
    expect(popularTier).toBeTruthy();
  });

  it('should render comparison table', () => {
    const table = element.querySelector('.pricing-page_table');
    expect(table).toBeTruthy();
  });

  it('should render FAQ section', () => {
    const faqSection = element.querySelector('.pricing-page_faq');
    expect(faqSection).toBeTruthy();
  });

  it('should render FAQ items', () => {
    const faqItems = element.querySelectorAll('.pricing-page_faq-item');
    expect(faqItems.length).toBeGreaterThan(0);
  });

  it('should render CTA section', () => {
    const ctaSection = element.querySelector('.pricing-page_cta');
    expect(ctaSection).toBeTruthy();
  });
});
