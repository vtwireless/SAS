﻿import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatDatepickerModule, MatNativeDateModule, MatPaginatorModule  } from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatCardModule } from '@angular/material/card';
import { AgmCoreModule } from '@agm/core';

import { AppComponent } from './app.component';
import { NavMenuComponent } from './nav-menu/nav-menu.component';
import { HomeComponent } from './home/home.component';
import { MapComponent } from './map/map.component';
import { NodeListComponent } from './node-list/node-list.component';
import { PUDetailsComponent } from './PU-details/PU-details.component';
import { NodeDetailsComponent } from './node-details/node-details.component';
import { GrantDetailsComponent } from './grant-details/grant-details.component';
import { CreateNodeComponent } from './create-node/create-node.component';
import { LoginComponent } from './login/login.component';
import { TiersComponent } from './tiers/tiers.component';
import { TierComponent } from './tier/tier.component';
import { AdminLoginComponent } from './admin-login/admin-login.component';
import { SchedulesComponent } from './schedules/schedules.component';
import { LogoutComponent } from './logout/logout.component';
import { JwtInterceptor } from './_helpers';
import { ErrorInterceptor } from './_helpers/error.interceptor';
import { NotFoundComponent } from './not-found/not-found.component';
import { AppRoutingModule } from './app-routing.module';
import { SepctrumInquiryRequestComponent } from './sepctrum-inquiry-request/sepctrum-inquiry-request.component';
import { FormsModule } from '@angular/forms';
import { NodeDeregisterComponent } from './node-deregister/node-deregister.component';
import { GrantRelinquishmentComponent } from './grant-relinquishment/grant-relinquishment.component';
import { GrantMessageComponent } from './grant-message/grant-message.component';
import { MatSortModule } from '@angular/material/sort';
import { InquiryLogsComponent } from './inquiry-logs/inquiry-logs.component';
import { SasTableComponentComponent } from './sas-table-component/sas-table-component.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import {AgmOverlays} from "agm-overlays";

@NgModule({
  declarations: [
    AppComponent,
    NavMenuComponent,
    HomeComponent,
    PUDetailsComponent,
    NodeDetailsComponent,
    NodeListComponent,
    CreateNodeComponent,
    LoginComponent,
    LogoutComponent,
    MapComponent,
    TiersComponent,
    TierComponent,
    SchedulesComponent,
    AdminLoginComponent,
    GrantDetailsComponent,
    NotFoundComponent,
    SepctrumInquiryRequestComponent ,
    NodeDeregisterComponent ,
    GrantRelinquishmentComponent ,
    GrantMessageComponent ,
    InquiryLogsComponent,
    SasTableComponentComponent
  ],

  imports: [
    BrowserModule.withServerTransition({appId: 'ng-cli-universal'}),
    AgmCoreModule.forRoot({
      apiKey: 'AIzaSyAg1LX7QqZa7ixpGqHO_B89q9YoIXBiz3w'
    }),
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    DragDropModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatSidenavModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatCheckboxModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatCardModule,
    AgmOverlays,
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
    { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

