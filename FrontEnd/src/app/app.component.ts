import { Component, ViewChild, AfterViewInit} from '@angular/core';
import { Router } from '@angular/router';
import { BreakpointObserver } from '@angular/cdk/layout';
import { MatSidenav } from '@angular/material/sidenav';

import { User } from './_models/models';
import { AuthenticationService } from './_services/authentication.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'app';
  currentUser: User;
  @ViewChild(MatSidenav, {static: false}) sidenav!: MatSidenav;
  loggedIn: boolean;
  username: string;

  constructor(
    private router: Router,
    private authenticationService: AuthenticationService,
    private observer: BreakpointObserver
  ) {
    this.authenticationService.currentUser.subscribe(x => this.currentUser = x);
    this.checkLogin();
  }
  
  checkLogin() {
    if (localStorage.getItem('currentUser')) {
      this.username = JSON.parse(localStorage.getItem('currentUser')).name;
      this.loggedIn = true;
    }
    else {
      this.loggedIn = false;
    }
  }

  ngAfterViewInit() {
    this.observer.observe(['(max-width: 1600px)']).subscribe((res) => {
        if (res.matches) {
          this.sidenav.mode = 'over';
          this.sidenav.close();
        } else {
          this.sidenav.mode = 'side';
          this.sidenav.open();
        }
      });
  }

  logout() {
    this.authenticationService.logout();
    this.username = "";
    this.loggedIn = false;
    this.router.navigate(['/login']);
  }
}
