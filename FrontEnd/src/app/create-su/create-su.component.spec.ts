import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateSUComponent } from './create-su.component';

describe('CreateSUComponent', () => {
  let component: CreateSUComponent;
  let fixture: ComponentFixture<CreateSUComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CreateSUComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateSUComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
