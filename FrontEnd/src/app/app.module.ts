import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider'

//import { MatSliderModule } from '@angular/material';

import { AppComponent } from './app.component';
import { NavMenuComponent } from './nav-menu/nav-menu.component';
import { HomeComponent } from './home/home.component';
import { MapComponent } from './map/map.component';
import { ContactComponent } from './contact/contact.component';
import { NodeListComponent } from './node-list/node-list.component';
import { GrantListComponent } from './grant-list/grant-list.component';
import { PUDetailsComponent } from './PU-details/PU-details.component';
import { SUDetailsComponent } from './SU-details/SU-details.component';
import { NodeDetailsComponent } from './node-details/node-details.component';
import { GrantDetailsComponent } from './grant-details/grant-details.component';
import { CreateSUComponent } from './create-su/create-su.component';
import { CreateNodeComponent } from './create-node/create-node.component';
import { LoginComponent } from './login/login.component';
import { TiersComponent } from './tiers/tiers.component';
import { TierComponent } from './tier/tier.component';
import { AdminLoginComponent } from './admin-login/admin-login.component';
import { SchedulesComponent } from './schedules/schedules.component';
import { CreateRequestComponent } from './create-request/create-request.component';
import { LogoutComponent } from './logout/logout.component';
import { JwtInterceptor } from './_helpers';
import { ErrorInterceptor } from './_helpers/error.interceptor';;
import { NotFoundComponent } from './not-found/not-found.component'
import { AppRoutingModule } from './app-routing.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    NavMenuComponent,
    HomeComponent,
    ContactComponent,
    CreateSUComponent,
    PUDetailsComponent,
    NodeDetailsComponent,
    SUDetailsComponent,
    NodeListComponent,
    GrantListComponent,
    CreateNodeComponent,
    LoginComponent,
    LogoutComponent,
    MapComponent,
    TiersComponent,
    TierComponent,
    SchedulesComponent,
    AdminLoginComponent,
    GrantDetailsComponent,
    CreateRequestComponent,
    NotFoundComponent
    // SocketComponent
  ],
  imports: [
    BrowserModule.withServerTransition({ appId: 'ng-cli-universal' }),
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    DragDropModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatSidenavModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
    { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

