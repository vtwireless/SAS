import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { InquiryLogsComponent } from './inquiry-logs.component';

describe('InquiryLogsComponent', () => {
  let component: InquiryLogsComponent;
  let fixture: ComponentFixture<InquiryLogsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ InquiryLogsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(InquiryLogsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
