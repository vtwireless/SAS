import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { User } from '../_models/models';
import { HttpRequestsService } from '../_services/http-requests.service';
import { SasTableComponentComponent } from '../sas-table-component/sas-table-component.component';


const SCHEMA = [
  {
    key: "timestamp",
    type: "epoch",
    label: "Timestamp"
  },
  {
    key: "cbsdId",
    type: "number",
    label: "CBSD ID"
  },
  {
    key: "inquiryLogID",
    type: "number",
    label: "Log ID"
  },
  {
    key: "requestLowFrequency",
    type: "frequency",
    label: "High Frequency(MHz)"
  },
  {
    key: "requestHighFrequency",
    type: "frequency",
    label: "High Frequency(MHz)"
  },
  {
    key: "responseCode",
    type: "number",
    label: "Response Code"
  },
  {
    key: "responseMessage",
    type: "text",
    label: "Response Message",
    minWidth: "200px"

  },
  {
    key: "availableChannels",
    type: "number",
    label: "Available Channels"
  },
  {
    key: "maxEIRP",
    type: "number",
    label: "Maximum EIRP"
  },
];


@Component({
  selector: 'app-inquiry-logs',
  templateUrl: './inquiry-logs.component.html',
  styleUrls: ['./inquiry-logs.component.css']
})


export class InquiryLogsComponent implements OnInit {

  logs: null;
  @ViewChild(SasTableComponentComponent, { static: false })
  table: SasTableComponentComponent;

  constructor(
    private httpRequests: HttpRequestsService,
    private route: ActivatedRoute,
    @Inject('BASE_URL') baseUrl: string,
    router: Router
  ) {
    if (localStorage.getItem('currentUser')) {
      let user = new User('', '', '');
      user = JSON.parse(localStorage.getItem('currentUser'));

      if (user.userType != 'ADMIN') {
        router.navigate(['/']);
      }
      else {
        this.httpRequests.getSpectrumInquiries().subscribe(
          (response) => {
            if ("spectrumInquiries" in response) {
              this.logs = response["spectrumInquiries"];
              this.table.setTable(this.logs, SCHEMA);
              this.table.setTableHeader("Spectrum Inquiries Logs")
            }
          },
          (error) => {
            this.logs = null;
            window.alert("Logs could not be fetched due to the following error:\n" + error);
          }
        )
      };
    }
  }
  ngOnInit(): void {
  }
}


export interface InquiryLog {
  inquiryLogID: any;
  timestamp: any;
  cbsdId: any;
  requestLowFrequency: any;
  requestHighFrequency: any;
  responseCode: any;
  responseMessage: any;
  availableChannels: any;
  ruleApplied: any;
  maxEIRP: any;
}