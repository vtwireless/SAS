import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AdminLoginComponent } from './admin-login/admin-login.component';
import { ContactComponent } from './contact/contact.component';
import { CreateNodeComponent } from './create-node/create-node.component';
import { CreateRequestComponent } from './create-request/create-request.component';
import { CreateSUComponent } from './create-su/create-su.component';
import { GrantDetailsComponent } from './grant-details/grant-details.component';
import { GrantListComponent } from './grant-list/grant-list.component';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { LogoutComponent } from './logout/logout.component';
import { MapComponent } from './map/map.component';
import { NodeDetailsComponent } from './node-details/node-details.component';
import { NodeListComponent } from './node-list/node-list.component';
import { PUDetailsComponent } from './PU-details/PU-details.component';
import { SchedulesComponent } from './schedules/schedules.component';
import { SUDetailsComponent } from './SU-details/SU-details.component';
import { TierComponent } from './tier/tier.component';
import { TiersComponent } from './tiers/tiers.component';
import { NotFoundComponent } from './not-found/not-found.component'
import {SepctrumInquiryRequestComponent} from './sepctrum-inquiry-request/sepctrum-inquiry-request.component';
import {NodeDeregisterComponent} from './node-deregister/node-deregister.component';
import {GrantRelinquishmentComponent} from './grant-relinquishment/grant-relinquishment.component';

const routes: Routes = [
  { path: '', component: HomeComponent, pathMatch: 'full' },
  { path: 'contact', component: ContactComponent },
  { path: 'create-su', component: CreateSUComponent },
  { path: 'PU-details/:id', component: PUDetailsComponent },
  { path: 'SU-details/:id', component: SUDetailsComponent },
  { path: 'node-details/:id', component: NodeDetailsComponent },
  { path: 'node-list', component: NodeListComponent },
  { path: 'grant-list', component: GrantListComponent },
  { path: 'create-node', component: CreateNodeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'tiers/:id', component: TiersComponent },
  { path: 'tier/:id', component: TierComponent },
  { path: 'schedules', component: SchedulesComponent },
  { path: 'logout', component: LogoutComponent },
  { path: 'map', component: MapComponent },
  { path: 'grant-details/:type/:id', component: GrantDetailsComponent },
  { path: 'create-request', component: CreateRequestComponent },
  { path: 'admin-login', component: AdminLoginComponent },
  { path: 'spectrum-inquiry-request', component: SepctrumInquiryRequestComponent },
  { path: 'node-deregister', component: NodeDeregisterComponent },
  { path: 'grant-relinquishment', component: GrantRelinquishmentComponent },

  {path: '**', component: NotFoundComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
