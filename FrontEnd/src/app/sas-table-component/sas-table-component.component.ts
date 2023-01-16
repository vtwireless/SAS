import { AfterViewInit, Component, OnInit, ViewChild, Input } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort, Sort } from '@angular/material/sort';
import { LiveAnnouncer } from '@angular/cdk/a11y';
// import { MatTable } from '@angular/material/table';
// import { MatFormFieldModule } from '@angular/material/form-field';
// import { MatInputModule } from '@angular/material/input';

@Component({
  selector: 'sas-table-component',
  templateUrl: './sas-table-component.component.html',
  // styleUrls: ['./sas-table-component.component.css']
  styleUrls: ['./table-component.scss']
})
export class SasTableComponentComponent implements AfterViewInit {

  dataSource = new MatTableDataSource([]);

  TABLE_DATA: [];
  TABLE_SCHEMA: TableSchema[];
  displayedColumns: string[];
  columnsSchema: any;
  tableHeader: any;
  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort, { static: true }) sort: MatSort;

  constructor(private _liveAnnouncer: LiveAnnouncer) { }

  setTable(data, schema: TableSchema[], freeSchema: boolean = false) {
    if (data.length > 0) {
      if (!freeSchema) {
        this.TABLE_DATA = data;
        this.TABLE_SCHEMA = schema;
        this.setTableProperties();
      } else {
        this.TABLE_DATA = data;
        console.log(data[0]);
        let schema = [];

        for (const [key, value] of Object.entries(data[0])) {
          schema.push({
            key: key,
            type: "text",
            label: key.toUpperCase() 
          });
        }
        this.TABLE_SCHEMA = schema;
        this.setTableProperties();
      }
    }
  }

  setTableProperties() {
    this.displayedColumns = this.TABLE_SCHEMA.map((col) => col.key);
    this.dataSource = new MatTableDataSource<any>(this.TABLE_DATA);
    this.columnsSchema = this.TABLE_SCHEMA;
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  setTableHeader(title) {
    this.tableHeader = title;
  }

  ngAfterViewInit(): void {
    if (this.TABLE_SCHEMA != null) {
      this.setTableProperties();
      this.setTableHeader(null);
    }
  }

  setType(data, type) {
    switch (type) {
      case "number":
        return data != null ? parseInt(data) : data;

      case "text":
        return data != null ? String(data) : data;

      case "epoch":
        let newDate = new Date(0);
        newDate.setUTCSeconds(parseInt(data));
        return data != null ? newDate.toLocaleString() : data;

      case "frequency":
        return data != null ? parseFloat(data) / 1e6 : data;

      default:
        return data;
    }
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }
}

interface TableSchema {
  key: any;
  type: any;
  label: any;
}
