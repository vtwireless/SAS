import { Component, Inject } from '@angular/core';
import { PrimaryUser, SecondaryUser, TierClass, TierClassAssignment, User, AppConstants } from '../_models/models';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpRequest } from '@angular/common/http';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
    selector: 'app-tiers',
    templateUrl: './tiers.component.html'
})
export class TiersComponent {

    TierClasses: Array<TierClass> = [];
    SecondaryUsers: Array<TierClassAssignment> = [];
    tier = new TierClass(null, null, null, null, null, null, null, null);
    showAll = false;
    showIndividual = false;
    tierID = '';
    GETAPI = AppConstants.GETURL;
    POSTAPI = AppConstants.POSTURL;
    MEGA = 1000000;
    GIGA = 1000000000;
    dissassociate = false;
    addSUs = false;
    model = new TierCreation(null, null, null);
    innerTierLevelArray: Array<number> = [];
    secondaryUsersToAdd: Array<SecondaryUser> = [];

    constructor(private httpRequests: HttpRequestsService, private route: ActivatedRoute, @Inject('BASE_URL') baseUrl: string, router: Router) {

        if(localStorage.getItem('currentUser')){
            let user = new User('', '', '');
            user = JSON.parse(localStorage.getItem('currentUser'));
            if(user.userType != 'ADMIN'){
                router.navigate(['/']);
            }
            else{
                this.route.params.subscribe(params => {
                    this.tierID = params.id;
                    this.showAll = false;
                    this.showIndividual = false;
                    if (this.tierID.toLowerCase() == "showall"){
                        this.showAll = true;

                    }
                    else{
                        this.showIndividual = true;
                    }
                    if(this.showAll){
                        this.httpRequests.getTierClass().subscribe(data => {
                            if(data['status'] == '1'){

                        this.TierClasses = data['tierClasses'];

                        for (var i = 0; i < this.TierClasses.length; i++){
                            if (this.TierClasses[i].tierUpperBand/this.MEGA > 1000){
                                this.TierClasses[i].tierUpperBand = this.TierClasses[i].tierUpperBand/this.GIGA;
                                this.TierClasses[i].tierLowerBand = this.TierClasses[i].tierLowerBand/this.GIGA;
                                this.TierClasses[i].range = 'GHz';
                            }
                            else {
                                this.TierClasses[i].tierUpperBand = this.TierClasses[i].tierUpperBand/this.MEGA;
                                this.TierClasses[i].tierLowerBand = this.TierClasses[i].tierLowerBand/this.MEGA;
                                this.TierClasses[i].range = 'MHz';
                            }
                        }
                    }
                    }, error => console.error(error));
            }
            else if (this.showIndividual){
                this.httpRequests.getTierClassID(this.tierID).subscribe(data => {
      if(data['status'] == '1'){
        this.tier = data['tierClass'];
                    if (this.tier.tierUpperBand/this.MEGA > 1000){
                        this.tier.tierUpperBand = this.tier.tierUpperBand/this.GIGA;
                        this.tier.tierLowerBand = this.tier.tierLowerBand/this.GIGA;
                        this.tier.range = 'GHz';
                    }
                    else {
                        this.tier.tierUpperBand = this.tier.tierUpperBand/this.MEGA;
                        this.tier.tierLowerBand = this.tier.tierLowerBand/this.MEGA;
                        this.tier.range = 'MHz';
                    }
                    var tempNumber = new Array();
                    var i = 0;
                    for (i = 0; i <= this.tier.maxTierNumber; i++){
                        tempNumber.push(i);
                    }
                    this.innerTierLevelArray = tempNumber;

                    this.SecondaryUsers = data['tierClassSUs'];
                }
                }, error => console.error(error));
            }


        });
}
}
}
toggleDissassociate(){
    this.dissassociate = !this.dissassociate;
}

toggleAddSU(){

    this.addSUs = !this.addSUs;
    if(this.addSUs){
        this.httpRequests.getSUsNotInTierClassByID(this.tierID).subscribe(data => {
        if(data['status'] == 1){
            this.secondaryUsersToAdd = data['secondaryUsers'];
        }
        }, error => console.error(error));
    }
    else{
        this.secondaryUsersToAdd = [];
    }
}

dissassociateSU(secondaryUser){
    if(confirm("Are you sure you want to delete "+ secondaryUser.secondaryUserName + ' from ' + this.tier.tierClassName + '?')) {
        this.httpRequests.deleteTierClassAssignmentsByID(secondaryUser).subscribe(data => {
            if(data['status'] == '1'){

                for(var i = 0; i == this.SecondaryUsers.length; i++){
                    if (this.SecondaryUsers[i].tierAssignmentID == secondaryUser.tierAssignmentID){
                        this.SecondaryUsers.splice(i, 1);
                        i--;
                    }
                }
            }


        }, error => console.error(error));

    }




}

createTierAssignment(){
    this.httpRequests.alterTierClassAssignmentByID(this.tierID, this.model).subscribe(data => {
        if(data['status'] == '1'){

            this.model = new TierCreation(null, null, null);
            this.addSUs = false;
            /*for(var i = 0; i < this.SecondaryUsers.length; i++){
              if (this.SecondaryUsers[i].tierAssignmentID == secondaryUser.tierAssignmentID){
                this.SecondaryUsers.splice(i, 1);
                i--;
              }
          }*/
      }


  }, error => console.error(error));
}



updateTierAssignment(secondaryUser, innerTierLevel){
    this.httpRequests.alterTierClassAssignmentByID(this.tierID, {secondaryUser, innerTierLevel}).subscribe(data => {
        if(data['status'] == '1'){

        }
        else{
            console.log("error occurred while updating");
        }


    }, error => console.error(error));
}

}

export class TierCreation {
    constructor( 
        public secondaryUserID: string,
        public tierClassID: string,
        public innerTierLevel: number,
        ) { }
}


