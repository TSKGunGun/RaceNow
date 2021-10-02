function download_CSV(a, tableElement, filename){
    var excaped = /,|\r?\n|\r|"/;
    var e = /"/g;
    var delmiter =",";
    
    var csv = [], r, c;
    for ( r=0;  r <= tableElement.rows.length-1; r++ ){
        var row = tableElement.rows[r];
        var rowdata = [];
        for( c=0; c <= row.cells.length-1; c++){
            var flddata = row.cells[c].textContent;
            if( excaped.test(flddata) ) {
                flddata = '"'+flddata.replace(e, '""')+'"';
            }
            rowdata.push(flddata);
        }
        csv.push(rowdata.join(delmiter));
    }

    var bom = new Uint8Array([0xEF, 0xBB, 0xBF]);
    var blob = new Blob([bom, csv.join('\n')], {"type": 'text/csv'});
    a.download = filename;
    a.href = window.URL.createObjectURL(blob);
}