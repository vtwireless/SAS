import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NodeDeregisterComponent } from './node-deregister.component';

describe('NodeDeregisterComponent', () => {
  let component: NodeDeregisterComponent;
  let fixture: ComponentFixture<NodeDeregisterComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NodeDeregisterComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NodeDeregisterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
