import { Component } from '@angular/core';
import { AuthenticationService } from '../_services/authentication.service';
import { User } from '../_models/models';
import { Subscription } from 'rxjs';


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  loggedIn = false;
  name = "";
  type = "";
  user = new User('', '', '');

  constructor() {
    if (localStorage.getItem('currentUser')) {
      this.loggedIn = true;
      this.user = JSON.parse(localStorage.getItem('currentUser'));
      this.name = this.user.name;
      
      if (this.user.userType == 'JUDGE') {
        this.type = 'Judge';
      }
      else if (this.user.userType == 'DIRECTOR') {
        this.type = 'Director';
      }
      else if (this.user.userType == 'ADMIN') {
        this.type = 'Administrator';
      }
    }
  }

  setStyleLogin() {
    return {
      'background-image': 'radial-gradient(#C8CDCDFF,' + '#111111FF' + ')',
      'background-repeat': 'no-repeat',
      'color': 'white',
      'width': '250px',
      'padding-top': '30px',
      'height': '100px',
      'font-size': '20px',
      'text-align': 'center',
      'border-radius': '10px',
      'margin': '10px',
      'display': 'inline-block'

    };
  }
  
  setStyleAdminLogin() {
    return {
      //'background': this.color1,
      'background-image': 'radial-gradient(#C8CDCDFF,' + '#111111FF' + ')',
      'background-repeat': 'no-repeat',
      'color': 'white',
      'width': '250px',
      'padding-top': '30px',
      'margin-left': '30px',
      'height': '100px',
      'font-size': '20px',
      'text-align': 'center',
      'border-radius': '10px',
      'margin': '10px',
      'display': 'inline-block'

    }
  }

}