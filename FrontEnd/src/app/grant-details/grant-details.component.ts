import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Node, SpectrumGrant, Heartbeat, User, AppConstants } from '../_models/models';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
  selector: 'app-grant-details',
  templateUrl: './grant-details.component.html',
})
export class GrantDetailsComponent {

 spectrumGrant: SpectrumGrant;
 Heartbeats: Array<Heartbeat> = [];
 GETAPI = AppConstants.GETURL;
 POSTAPI = AppConstants.POSTURL;
 public grantID;
 public type;
 public active = false;
 public logged = false;
 public deleting = false;
 public message = "";
 public deleteConfrim = "";
 model = new Confirm('');

  constructor(private httpRequests: HttpRequestsService, private router: Router, private route: ActivatedRoute) {

          if(localStorage.getItem('currentUser')){
        let user = new User('', '', '');
        this.model = new Confirm('');
        user = JSON.parse(localStorage.getItem('currentUser'));
        if(user.userType != 'ADMIN'){
            this.router.navigate(['/']);
          }
          else{
          this.route.params.subscribe(params => this.grantID = params.id);
          this.route.params.subscribe(params => this.type = params.type);

          if (this.type == "active"){
              this.active = true;
          }
          else if (this.type == "logged"){
              this.logged = true;
            }
          }
        
        if (this.active){
                this.httpRequests.getGrantByID(this.grantID).subscribe(data => {
                    if(data['status'] == '1'){
                        this.spectrumGrant = data['spectrumGrant'];
                        this.Heartbeats = data['heartbeats'];

                    }
                }, error => console.error(error));


      }
        else if (this.logged){
      this.httpRequests.getGrantLogByID(this.grantID).subscribe(result => {
          this.spectrumGrant = result['grantLog'];
          this.Heartbeats = result['heartbeats'];
      }, error => console.error(error));

      }
      else{
        console.log('No type specified.');
      }
    }
    }

        public deleteGrant(){
          if(this.deleting ){
            if(this.model.confirm == "CONFIRM"){
          this.deleting = false;
          this.model.confirm = "";
          this.message = "Deleting, please wait...";
          this.httpRequests.logGrant(this.grantID).subscribe(data => {
        console.log(data);
          if(data['status'] == '1'){

            this.message = "Grant deleted successfully! Please do not redirect";
                        setTimeout(() =>
            {
               this.message = "";
               this.router.navigate(['/']);
            },
            2000);

          }
      }, error => console.error(error));
        }
              else{
        this.message = "Please type CONFIRM in the box to delete and log the grant";
      }
      }

    }

      public cancelDelete(){
        this.deleting = false;
        this.message = "";
      }

      public showDelete(){
         this.deleting = true;
         this.message = "Enter 'CONFIRM' in the box above and click 'Confirm'.";
      }



}

export class Confirm{
    constructor(
    public confirm: string,
  ) {  }
}