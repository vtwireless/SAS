import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpRequestsService } from '../_services/http-requests.service';
import { Node, SpectrumInquiryRequest, User, freqRange } from '../_models/models';

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
    this.chosenFreqRanges.push(new freqRange(this.lowFreq, this.highFreq));
    console.log(this.chosenFreqRanges);
    console.log(this.chosenFreqRanges[0].lowFrequency);

    console.log(this.lowFreq + " - " + this.highFreq);
    this.lowFreq = 0;
    this.highFreq = 0;

  }

  newRequest() {
    this.modelSpectrumInquiryRequest = new SpectrumInquiryRequest(
        null,null
    );

    this.chosenFreqRanges = []
  }

  onSubmit(){
    this.submitted = true;
    this.chosenFreqRanges.push(new freqRange(this.lowFreq, this.highFreq));
    this.lowFreq = 0;
    this.highFreq = 0;
    // console.log(this.chosenFreqRanges[0]);
    this.modelSpectrumInquiryRequest.inquiredSpectrum = this.chosenFreqRanges;
    // console.log(this.chosenFreqRanges);
    // console.log(this.modelSpectrumInquiryRequest);

    const user = JSON.parse(localStorage.getItem('currentUser'));
    this.httpRequests.spectrumInqRequest(this.modelSpectrumInquiryRequest).subscribe(
        (data) => {
          let val = data['spectrumInquiryResponse'];
          this.response = val[0]['response']['responseMessage'];
          console.log(data);
          if (data['status'] == '1') {

          }
        },
        (error) => console.error(error)
    );

  }

}
