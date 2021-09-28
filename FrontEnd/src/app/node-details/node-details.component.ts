import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Node, User, AppConstants } from '../_models/models';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
    selector: 'app-node-details',
    templateUrl: './node-details.component.html',
})
export class NodeDetailsComponent {

    Node: Node;
    GETAPI = AppConstants.GETURL;
    POSTAPI = AppConstants.POSTURL;
    public nodeID;
    locationValid = true;
    public editing = false;
    message = "";
    trustLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    nodeTypes = ['VT-CRTS-Node', 'VT-Wireless-Registered Radar', 'Mobile-Device'];
    statuses = ['ACTIVE', 'INACTIVE', 'OFFLINE', 'ONLINE', 'DAMAGED', 'OTHER'];
    model = new Node(null, null, null, null, null, null, null, null, null, null, null, null, null, )
    information = '';
    constructor(private httpRequests: HttpRequestsService, private router: Router, private route: ActivatedRoute) {
        this.Node = new Node(null,'','',null,'',null,null,null,null,'',null,'','');
        if(localStorage.getItem('currentUser')){
            let user = new User('', '', '');
            user = JSON.parse(localStorage.getItem('currentUser'));
            if(user.userType != 'ADMIN'){
                this.router.navigate(['/']);
            }
            else{
                this.route.params.subscribe(params => this.nodeID = params.id);
            }
        }

        this.httpRequests.getNodeByID(this.nodeID).subscribe(data => {
            if(data['status'] == '1'){

                this.Node = data['node'];
            }
        }, error => console.error(error));

    }

    public editNode(){
        if(this.editing && this.locationValid){

            this.editing = false;
            this.httpRequests.updateNode(this.model).subscribe(data => {
                if(data['status'] == '1'){

                    this.message = "Node updated successfully!";
                    setTimeout(() =>
                    {
                        this.message = "";
                    },
                    3000);

                }
            }, error => console.error(error));
        }
        else{
            this.message = "An Error occurred";
            this.editing = true;
            this.model = this.Node;
        }
    }

    public cancelEdit(){
        this.editing = false;
    }

    public updateFrequencies() {
        if (this.model.maxFrequency < this.model.minFrequency){
            this.model.maxFrequency = this.model.minFrequency;
        }
    }
    public updateSampleRate() {
        if (this.model.maxSampleRate < this.model.minSampleRate){
            this.model.maxSampleRate = this.model.minSampleRate;
        }
    }
    public checkLocationValid(){
        this.model.location = this.model.location.replace(' ','');
        this.model.location = this.model.location.replace(/[abcdefghijklmnopqrstuvwxyz!@#$%^&*();:<>?]/gi,'');
        var split = this.model.location.split(",");
        if(split.length == 2){
            if(Number(split[0])<=180 && Number(split[0])>=-180 && (Number(split[1])<=90 && Number(split[1])>=-90) && split[0].length>5 && split[1].length>5){
                this.locationValid = true;
            }
            else{
                this.locationValid = false;
            }
        }
        else {
            this.locationValid = false;
        }
        //console.log(this.locationValid);
    }


}