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

  addRange(){
    this.chosenFreqRanges.push(new freqRange(this.lowFreq, this.highFreq));
    this.lowFreq = 0;
    this.highFreq = 0;
  }

  newRequest() {
    this.modelSpectrumInquiryRequest = new SpectrumInquiryRequest(
        null,null
    );
  }

  onSubmit(){
    this.submitted = true;
    this.chosenFreqRanges.push(new freqRange(this.lowFreq, this.highFreq));
    this.lowFreq = 0;
    this.highFreq = 0;
    this.modelSpectrumInquiryRequest.selectedFrequencyRanges = this.chosenFreqRanges;
    console.log(this.chosenFreqRanges);
    console.log(this.modelSpectrumInquiryRequest);

    const user = JSON.parse(localStorage.getItem('currentUser'));

    this.httpRequests.spectrumInqRequest(this.modelSpectrumInquiryRequest).subscribe(
        (data) => {
          if (data['status'] == '1') {
            this.router.navigate(['/']);
          }
        },
        (error) => console.error(error)
    );

  }

}
