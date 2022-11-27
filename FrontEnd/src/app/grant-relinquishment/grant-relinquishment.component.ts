import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {User, RelinquishmentRequest} from '../_models/models';
import { HttpRequestsService } from '../_services/http-requests.service';


@Component({
  selector: 'app-grant-relinquishment',
  templateUrl: './grant-relinquishment.component.html',
  styleUrls: ['./grant-relinquishment.component.css']
})
export class GrantRelinquishmentComponent implements OnInit {

  cbsdIDList = [];
  grantIDList = [];
  submitted = false;
  creatorID = '';
  relinquishmentRequest = new RelinquishmentRequest(null,null);
  responseMessage = '';


  constructor(
      private httpRequests: HttpRequestsService,
      private router: Router
  ) {

    if (localStorage.getItem('currentUser')) {
      let user = new User('', '', '');
      user = JSON.parse(localStorage.getItem('currentUser'));
      if (user.userType != 'ADMIN' && user.userType != 'SU') {
        this.router.navigate(['/']);
      } else {
        this.creatorID = user.id;
      }
    }

    this.httpRequests.getAllNodes().subscribe(
        data => {
          if (data['status'] == '1') {
            for (const node of data['nodes']) {
              this.cbsdIDList.push(node.cbsdID);
            }
          }

        }, error => console.error(error)
    );

    this.httpRequests.getSpectrumGrants().subscribe(
        data => {
          if(data['status']=='1'){
            for(const grant of data['spectrumGrants']){
              this.grantIDList.push(grant.grantId);
            }
          }
        }, error => console.log(error)
    )

    console.log(this.cbsdIDList);
    console.log(this.grantIDList);


  }

  ngOnInit() {
  }

  newRequest() {
    this.relinquishmentRequest = new RelinquishmentRequest(
        null, null
    );
    this.responseMessage = '';
  }

  onSubmit(){
    this.submitted = true;
    console.log(this.relinquishmentRequest);
    const user = JSON.parse(localStorage.getItem('currentUser'));

    this.httpRequests.grantRelinquishmentRequest(this.relinquishmentRequest).subscribe(
        (data)=> {
          console.log(data['relinquishmentResponse'][0]);
          this.responseMessage = data['relinquishmentResponse'][0]['response']['message'];
        }
    )
  }



}
