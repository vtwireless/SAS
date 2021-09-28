/*

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatSnackBarModule } from '@angular/material/snack-bar';

// import { CoreModule } from '@app/core/core.module';
import { ApiGatewayService } from '../_services/api-gateway.service';
import { CoreService } from './core.service';
import { MapService } from './map.service';
import { MinuteManService } from './mm.service';
import { ReportsService } from './reports.service';
import { ActivityLogService } from './activity-log.service';
import { AuthInterceptor } from './auth-interceptor';
import { MmcService } from './mmc.service';
import { OrderService } from './order.service';
import { MissionService } from './mission.service';
import { TravelerService } from './traveler.service';
import { FlightAwareService } from './flight-aware.service';

@NgModule({
  imports: [
    CommonModule,
    CoreModule,
    HttpClientModule,
    MatSnackBarModule
  ],
  declarations: [],
  providers: [CoreService, ApiGatewayService, MapService, MinuteManService, ActivityLogService, MmcService, ReportsService, {
    provide: HTTP_INTERCEPTORS,
    useClass: AuthInterceptor,
    multi: true
  }, OrderService, MissionService, TravelerService, FlightAwareService]
})
export class GatewayModule { }

*/
