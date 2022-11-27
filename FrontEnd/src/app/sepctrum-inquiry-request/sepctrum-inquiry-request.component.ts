import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MatPaginator } from '@angular/material/paginator';
import { HttpRequestsService } from '../_services/http-requests.service';
import { Node, SpectrumInquiryRequest, User,ResponseObj, AvailableChannel, freqRange, SpectrumInquiryResponse } from '../_models/models';
import { MatTableDataSource } from '@angular/material/table';


@Component({
  selector: 'app-sepctrum-inquiry-request',
  templateUrl: './sepctrum-inquiry-request.component.html',
  styleUrls: ['./sepctrum-inquiry-request.component.css']
})
export class SepctrumInquiryRequestComponent implements OnInit {

  cbsdIDList = [];
  modelSpectrumInquiryRequest = new SpectrumInquiryRequest(
      null,null
  );
  lowFreq = 0;
  highFreq = 0;
  chosenFreqRanges = [];
  creatorID = '';
  submitted = false;
  response = '';
  spectrumResponse: SpectrumInquiryResponse[] = [];
  dataSource = new MatTableDataSource<SpectrumInquiryResponse>(this.spectrumResponse);
  @ViewChild(MatPaginator, { static: false }) paginator: MatPaginator;

  displayedColumns: string[] = [
    'cbsdId', 'responseCode', 'responseMessage', 'channelType', 'maxEirp', 'ruleApplied', 'grantRequest', 'frequencyRange'
  ];


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

  ngOnInit(){

  }
  currList = [];
  currSubList = [];
  currLowFreq = 0;
  currHighFreq = 0;

  addRange(){
    this.currLowFreq =  this.lowFreq;
    this.currHighFreq = this.highFreq;

    this.currSubList.push(this.currLowFreq);
    this.currSubList.push(this.currHighFreq);
    this.currList.push(this.currSubList);
    this.chosenFreqRanges.push(new freqRange(this.lowFreq * 1000000, this.highFreq * 1000000));
    // console.log(this.chosenFreqRanges);
    // console.log(this.chosenFreqRanges[0].lowFrequency);

    // console.log(this.lowFreq + " - " + this.highFreq);
    this.lowFreq = 0;
    this.highFreq = 0;

  }

  newRequest() {
    this.modelSpectrumInquiryRequest = new SpectrumInquiryRequest(
        null,null
    );

    this.chosenFreqRanges = []

  }

    clearResponse(){
        this.dataSource.data = [];
        this.spectrumResponse = [];
    }

  onSubmit(){
      // this.modelSpectrumInquiryRequest.cbsdId = 1;
    this.submitted = true;
    this.chosenFreqRanges.push(new freqRange(this.lowFreq * 1000000, this.highFreq * 1000000));
    this.lowFreq = 0;
    this.highFreq = 0;
    this.modelSpectrumInquiryRequest.inquiredSpectrum = this.chosenFreqRanges;
    // console.log(this.chosenFreqRanges);
    console.log(this.modelSpectrumInquiryRequest);

    const user = JSON.parse(localStorage.getItem('currentUser'));
    this.httpRequests.spectrumInqRequest(this.modelSpectrumInquiryRequest).subscribe(
        (data) => {
          let resp = data['spectrumInquiryResponse'];
          // console.log(resp);

          for(let i=0;i<resp.length;i++){
            let currentResponse = new SpectrumInquiryResponse(null,0,null);

            if(resp[i].response.responseCode!=="0"){
                currentResponse.cbsdId  = resp[i]['cbsdId'];
                currentResponse.response = new ResponseObj(null,null);
                currentResponse.response.responseCode = resp[i]['response']['responseCode'];
                currentResponse.response.responseMessage = resp[i]['response']['responseMessage'];
                this.spectrumResponse.push(currentResponse);
            }


            else{

                for(let j=0;j<resp[i].availableChannel.length;j++){
                    let currentResponse = new SpectrumInquiryResponse(null,0,null);
                    currentResponse.cbsdId  = resp[i]['cbsdId'];
                    currentResponse.response = new ResponseObj(null,null);
                    currentResponse.response.responseCode = resp[i]['response']['responseCode'];
                    currentResponse.response.responseMessage = resp[i]['response']['responseMessage'];
                    let currChannel = new AvailableChannel("", null,null,0,"");
                    currChannel.channelType = resp[i]['availableChannel'][j]['channelType'];
                    currChannel.frequencyRange = new freqRange(null,null);
                    currChannel.frequencyRange.lowFrequency = resp[i]['availableChannel'][j]['frequencyRange']['lowFrequency'];
                    currChannel.frequencyRange.highFrequency = resp[i]['availableChannel'][j]['frequencyRange']['highFrequency'];
                    currChannel.grantRequest = resp[i]['availableChannel'][j]['grantRequest'];
                    currChannel.maxEirp = resp[i]['availableChannel'][j]['maxEirp'];
                    currChannel.ruleApplied = resp[i]['availableChannel'][j]['ruleApplied'];
                    currentResponse.availableChannel = [];
                    currentResponse.availableChannel.push(currChannel);
                    this.spectrumResponse.push(currentResponse);
                    console.log(currentResponse);

                }
                console.log(this.spectrumResponse);

            }


          }
          this.dataSource.data = this.spectrumResponse;
          // console.log(this.dataSource.data);
          // console.log(this.spectrumResponse);
          this.response = resp[0]['response']['responseMessage'];
          // console.log(data);
          if (data['status'] == '1') {

          }
        },
        (error) => console.error(error)
    );

  }

}
