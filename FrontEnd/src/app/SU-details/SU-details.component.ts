import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SecondaryUser, TierClass, TierClassAssignment, GrantRequest, GrantLog, SpectrumGrant, User, AppConstants } from '../_models/models';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
    selector: 'app-SU-details',
    templateUrl: './SU-details.component.html',
})
export class SUDetailsComponent {

    secondaryUser: SecondaryUser;
    TierClasses: Array<TierClassAssignment> = [];
    grantRequests: Array<GrantRequest> = [];
    spectrumGrants: Array<SpectrumGrant> = [];
    grantLogs: Array<GrantLog> = [];
    GETAPI = AppConstants.GETURL;
    POSTAPI = AppConstants.POSTURL;
    public userID;
    isSU = 0;
    MEGA = 1000000;
    GIGA = 1000000000;
    information = '';
    constructor(private httpRequests: HttpRequestsService, private router: Router, private route: ActivatedRoute) {

        if(localStorage.getItem('currentUser')){
            let user = new User('', '', '');
            user = JSON.parse(localStorage.getItem('currentUser'));
            if(user.userType != 'ADMIN' && user.userType !='SU'){
                this.router.navigate(['/']);
            }
            else if(user.userType =='SU'){
                this.isSU = 1;
                this.userID = user.id;
            }
            else{
                this.route.params.subscribe(params => this.userID = params.id);
            }
        }

        this.httpRequests.getSecondaryUserByID(this.userID).subscribe(data => {
                if(data['status'] == '1'){


                    this.secondaryUser = data['secondaryUser'];
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

                    this.httpRequests.getAllGrantsBySUID(this.userID).subscribe(data => {
                if(data['status'] == 1){
                    this.grantRequests = data['grantRequests'];
                    this.spectrumGrants = data['spectrumGrants'];
                    this.grantLogs = data['grantLogs'];

                    for (var i = 0; i < this.grantRequests.length; i++){
                        if (this.grantRequests[i].maxFrequency/this.MEGA > 1000){
                            this.grantRequests[i].maxFrequency = this.grantRequests[i].maxFrequency/this.GIGA;
                            this.grantRequests[i].minFrequency = this.grantRequests[i].minFrequency/this.GIGA;
                            this.grantRequests[i].preferredFrequency = this.grantRequests[i].preferredFrequency/this.GIGA;
                            this.grantRequests[i].range = 'GHz';
                        }
                        else {
                            this.grantRequests[i].maxFrequency = this.grantRequests[i].maxFrequency/this.MEGA;
                            this.grantRequests[i].minFrequency = this.grantRequests[i].minFrequency/this.MEGA;
                            this.grantRequests[i].preferredFrequency = this.grantRequests[i].preferredFrequency/this.MEGA;
                            this.grantRequests[i].range = 'MHz';
                        }
                    }
                    for (var i = 0; i < this.spectrumGrants.length; i++){
                        if (this.spectrumGrants[i].frequency/this.MEGA > 1000){
                            this.spectrumGrants[i].frequency = this.spectrumGrants[i].frequency/this.GIGA;
                            this.spectrumGrants[i].requestMinFrequency = this.spectrumGrants[i].requestMinFrequency/this.GIGA;
                            this.spectrumGrants[i].requestMaxFrequency = this.spectrumGrants[i].requestMaxFrequency/this.GIGA;
                            this.spectrumGrants[i].requestPreferredFrequency = this.spectrumGrants[i].requestPreferredFrequency/this.GIGA;
                            this.spectrumGrants[i].range = 'GHz';
                        }
                        else {
                            this.spectrumGrants[i].frequency = this.spectrumGrants[i].frequency/this.MEGA;
                            this.spectrumGrants[i].requestMinFrequency = this.spectrumGrants[i].requestMinFrequency/this.MEGA;
                            this.spectrumGrants[i].requestMaxFrequency = this.spectrumGrants[i].requestMaxFrequency/this.MEGA;
                            this.spectrumGrants[i].requestPreferredFrequency = this.spectrumGrants[i].requestPreferredFrequency/this.MEGA;
                            this.spectrumGrants[i].range = 'MHz';
                        }
                    }
                    for (var i = 0; i < this.grantLogs.length; i++){
                        if (this.grantLogs[i].frequency/this.MEGA > 1000){
                            this.grantLogs[i].frequency = this.grantLogs[i].frequency/this.GIGA;
                            this.grantLogs[i].requestMinFrequency = this.grantLogs[i].requestMinFrequency/this.GIGA;
                            this.grantLogs[i].requestMaxFrequency = this.grantLogs[i].requestMaxFrequency/this.GIGA;
                            this.grantLogs[i].requestPreferredFrequency = this.grantLogs[i].requestPreferredFrequency/this.GIGA;
                            this.grantLogs[i].range = 'GHz';
                        }
                        else {
                            this.grantLogs[i].frequency = this.grantLogs[i].frequency/this.MEGA;
                            this.grantLogs[i].requestMinFrequency = this.grantLogs[i].requestMinFrequency/this.MEGA;
                            this.grantLogs[i].requestMaxFrequency = this.grantLogs[i].requestMaxFrequency/this.MEGA;
                            this.grantLogs[i].requestPreferredFrequency = this.grantLogs[i].requestPreferredFrequency/this.MEGA;
                            this.grantLogs[i].range = 'MHz';
                        }
                    }
                }
            }, error => console.error(error));
}




deleteGrantRequest(grantRequest){
    if(confirm("Are you sure you want to delete request with ID: "+ grantRequest.requestID + '?')) {
        this.httpRequests.deleteGrantRequest(grantRequest.requestID).subscribe(data => {
            if(data['status'] == '1'){

                setTimeout(() =>
                {
                    this.router.navigate(['/SU-details/'+this.userID]);
                },
                2000);
            }


        }, error => console.error(error));

    }



}

}