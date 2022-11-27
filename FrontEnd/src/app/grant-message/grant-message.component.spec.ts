import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GrantMessageComponent } from './grant-message.component';

describe('GrantMessageComponent', () => {
  let component: GrantMessageComponent;
  let fixture: ComponentFixture<GrantMessageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GrantMessageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GrantMessageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
