import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { Router, ActivatedRoute } from '@angular/router';

import { PrimaryUser, SecondaryUser, Node, User, AppConstants } from '../_models/models';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
    selector: 'app-node-list',
    templateUrl: './node-list.component.html',
    styleUrls: ['./node-list.component.css']
})
export class NodeListComponent implements AfterViewInit {
    checkActive:Boolean = false;
    Nodes: NodeList[] = [];
    dataSource = new MatTableDataSource<NodeList>(this.Nodes);
    @ViewChild(MatPaginator, { static: false }) paginator: MatPaginator;

    displayedColumns: string[] = [
        'nodeID', 'nodeName', 'location', 'trustLevel', 'freqRange', 'sampleRange',
        'nodeType', 'mobility', 'status'
    ];

    constructor(private httpRequests: HttpRequestsService, router: Router) {
        if (localStorage.getItem('currentUser')) {
            let user = new User('', '', '');
            user = JSON.parse(localStorage.getItem('currentUser'));
            if (user.userType != 'ADMIN') {
                router.navigate(['/']);
            }
        }

        this.httpRequests.getAllNodes().subscribe(
            data => {
                if (data['status'] == '1') {
                    for (const node of data['nodes']) {
                        var node_model: NodeList = {
                            nodeID: '',
                            nodeName: '',
                            location: '',
                            trustLevel: '',
                            freqRange: '',
                            sampleRange: '',
                            nodeType: '',
                            mobility: '',
                            status: ''
                        };
                        node_model.nodeID = node.cbsdID;
                        node_model.nodeName = node.nodeName;
                        node_model.location = node.location;
                        node_model.trustLevel = node.trustLevel;
                        node_model.freqRange = (node.minFrequency).toString() + "-" + (node.maxFrequency).toString();
                        node_model.sampleRange = node.minSampleRate.toString() + "-" + node.maxSampleRate.toString();
                        node_model.nodeType = node.nodeType;
                        node_model.mobility = node.mobility == "true" ? 'Yes' : 'No';
                        node_model.status = node.status;
                        if(node_model.status === "ACTIVE"){
                            this.checkActive = true;
                        }
                        this.Nodes.push(node_model);
                    }
                }
                this.dataSource.data = this.Nodes;
            }, error => console.error(error)
        );
    }

    ngAfterViewInit() {
        this.dataSource.paginator = this.paginator;
    }
}

export interface NodeList {
    nodeID: string;
    nodeName: string;
    location: string;
    trustLevel: string;
    freqRange: string;
    sampleRange: string;
    nodeType: string;
    mobility: string;
    status: string;
}