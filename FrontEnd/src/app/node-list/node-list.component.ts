import { Component, Inject } from '@angular/core';
import { PrimaryUser, SecondaryUser, Node, User, AppConstants } from '../_models/models';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
    selector: 'app-node-list',
    templateUrl: './node-list.component.html'
})
export class NodeListComponent {

    Nodes: Array<Node> = [];
    API = AppConstants.GETURL;

    constructor(private httpRequests: HttpRequestsService, @Inject('BASE_URL') baseUrl: string, router: Router) {

        if(localStorage.getItem('currentUser')){
            let user = new User('', '', '');
            user = JSON.parse(localStorage.getItem('currentUser'));
            if(user.userType != 'ADMIN'){
                router.navigate(['/']);
            }
        }

        this.httpRequests.getAllNodes().subscribe(data => {
            if(data['status'] == '1'){

                this.Nodes = data['nodes'];
            }
        }, error => console.error(error));

    }

}