import { AfterViewInit, Component, OnInit, ViewChild, Input } from '@angular/core';
// import { MatPaginator } from '@angular/material/paginator';
// import { MatSort } from '@angular/material/sort';
// import { MatTable } from '@angular/material/table';
// import { MatFormFieldModule } from '@angular/material/form-field';
// import { MatInputModule } from '@angular/material/input';

@Component({
  selector: 'sas-table-component',
  templateUrl: './sas-table-component.component.html',
  styleUrls: ['./sas-table-component.component.css']
})
export class SasTableComponentComponent implements AfterViewInit {

  TABLE_DATA: [];
  TABLE_SCHEMA: TableSchema[];
  displayedColumns: string[];
  dataSource: any;
  columnsSchema: any;
  tableHeader: any;

  setTable (data, schema: TableSchema[]) {
    this.TABLE_DATA = data;
    this.TABLE_SCHEMA = schema;
    this.setTableProperties();
  }

  setTableProperties() {
    this.displayedColumns = this.TABLE_SCHEMA.map((col) => col.key);
    this.dataSource = this.TABLE_DATA;
    this.columnsSchema = this.TABLE_SCHEMA;
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
        return data != null ? String(data): data;
      
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
}

interface TableSchema {
  key: any;
  type: any;
  label: any;
}
