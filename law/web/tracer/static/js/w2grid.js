$(function () {

    var sel ;

    var processed;

    $('#grid').w2grid({
        name: 'grid',
        header: 'List of Names',
        show : {
            header         : false,
            toolbar        : true,
            footer         : true,
            columnHeaders  : true,
            lineNumbers    : true,
            expandColumn   : false,
            selectColumn   : false,
            emptyRecords   : true,
            toolbarReload  : false,
            toolbarColumns : true,
            toolbarSearch  : true,
            toolbarAdd     : false,
            toolbarEdit    : true,
            toolbarDelete  : false,
            toolbarSave    : false,
            selectionBorder: true,
            recordTitles   : true,
            skipRecords    : false
        },
        columns: [
            { field: 'cluster', caption: 'Cluster', size: '9%', sortable: true },
            { field: 'status', caption: 'Status', size: '13%', sortable: true },
            { field: 'run_start_time', caption: 'Run Start Time', size: '22%', sortable: true},
            { field: 'run_end_time', caption: 'Run End Time', size: '22%'},
            { field: 'run_secs', caption: 'Run Time(Sec)', size: '15%', sortable: true },
            { field: 'uid', caption: 'Unique ID', size: '19%', sortable: true },
        ],
        postData : JSON.parse(JSON.stringify(({datefilter:$('#date').val(), cluster:$('#cluster').val()})))

    });
    if (processed != 'Y'){
        w2ui['grid'].load('/apiv1/tracer/tracergrid/');
    }

    DrawChart();

    $("#style9").submit( function( event ){
      event.preventDefault();
      processed = 'Y';
      var sdate = '';
      sdate =  $('#date').val();
      sdate = (sdate.length==0?'*':sdate);
      var scluster = '';
      scluster = $('#cluster').val();
      scluster = (scluster.length==0?'*':scluster);
      postData = JSON.stringify({'Date': sdate, 'Cluster':scluster})

      var url =  '/apiv1/tracer/tracergrid/' + sdate + '/' + scluster;
      w2ui['grid'].load(url);

      DrawChart();

    });

});
