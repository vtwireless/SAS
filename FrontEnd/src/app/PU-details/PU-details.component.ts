import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { PrimaryUser, PrimaryUserActivity, User, AppConstants } from '../_models/models';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
    selector: 'app-details',
    templateUrl: './PU-details.component.html',
})
export class PUDetailsComponent {

    PrimaryUser: PrimaryUser;
    activities: Array<PrimaryUserActivity> = [];
    GETAPI = AppConstants.GETURL;
    POSTAPI = AppConstants.POSTURL;
    public userID;
    isPU = 0;
    information = '';
    constructor(private httpRequests: HttpRequestsService, private router: Router, private route: ActivatedRoute) {

        if(localStorage.getItem('currentUser')){
            let user = new User('', '', '');
            user = JSON.parse(localStorage.getItem('currentUser'));
            if(user.userType != 'ADMIN' && user.userType !='PU'){
                this.router.navigate(['/']);
            }
            else if(user.userType =='PU'){
                this.isPU = 1;
                this.userID = user.id;
            }
            else{
                this.route.params.subscribe(params => this.userID = params.id);
            }
        }
        this.httpRequests.getPrimaryUserByID(this.userID).subscribe(data => {
            if(data['status'] == '1'){

                this.PrimaryUser = data['primaryUser'];
            }
        }, error => console.error(error));

        this.httpRequests.getPrimaryUserActivityByID(this.userID).subscribe(data => {
            if(data['status'] == '1'){
                this.activities = data['primaryUserActivities'];
                console.log(this.activities);
            }
        }, error => console.error(error));
    }


}