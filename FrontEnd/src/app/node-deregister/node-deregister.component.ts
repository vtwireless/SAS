import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {DeregistrationRequest, User} from '../_models/models';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
  selector: 'app-node-deregister',
  templateUrl: './node-deregister.component.html',
  styleUrls: ['./node-deregister.component.css']
})
export class NodeDeregisterComponent implements OnInit {

  creatorID = '';
  cbsdIDList = [];
  deregistrationRequest = new DeregistrationRequest(
      null
  );
  submitted = false;
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
  }

  ngOnInit() {

  }

  newRequest() {
    this.deregistrationRequest = new DeregistrationRequest(
        null
    );
    this.responseMessage = '';
  }

  onSubmit(){
    this.submitted = true;
    console.log(this.deregistrationRequest);
    const user = JSON.parse(localStorage.getItem('currentUser'));

    this.httpRequests.nodeDeregistrationRequest(this.deregistrationRequest).subscribe(
        (data)=> {
          console.log(data);
          this.responseMessage = data['message'];
        }
    )
  }

}
