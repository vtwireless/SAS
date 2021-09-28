import { Component } from '@angular/core';
import { User } from '../_models/models';

@Component({
  selector: 'app-nav-menu',
  templateUrl: './nav-menu.component.html',
  styleUrls: ['./nav-menu.component.css']
})
export class NavMenuComponent {
  isExpanded = false;
  userType = '';
  loggedIn = false;
  constructor(){
    this.reload();
  }
  reload(){
    if(localStorage.getItem('currentUser')){
        let user = new User('', '', '');
        user = JSON.parse(localStorage.getItem('currentUser'));
        this.userType = user.userType;
        this.loggedIn = true;
    }
    else{
      this.loggedIn = false;
    }
  }

  collapse() {
    this.isExpanded = false;
  }

  toggle() {
    this.isExpanded = !this.isExpanded;
  }
  
  clearStudent() {
                localStorage.removeItem('studentID');
  }
}
