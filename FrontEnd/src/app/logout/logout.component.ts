import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
	selector: 'app-home',
	templateUrl: './logout.component.html',
})
export class LogoutComponent {
	loggedIn = false;

	constructor(private router: Router) {
		if (localStorage.getItem('currentUser')) {
			localStorage.removeItem('currentUser');
			window.location.reload();
		} else {
			setTimeout(() => {
				this.router.navigate(['/']);
			}, 1500); //3s
		}
	}
}
