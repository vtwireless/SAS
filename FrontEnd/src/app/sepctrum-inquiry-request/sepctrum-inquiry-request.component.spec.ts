import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SepctrumInquiryRequestComponent } from './sepctrum-inquiry-request.component';

describe('SepctrumInquiryRequestComponent', () => {
  let component: SepctrumInquiryRequestComponent;
  let fixture: ComponentFixture<SepctrumInquiryRequestComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SepctrumInquiryRequestComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SepctrumInquiryRequestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
