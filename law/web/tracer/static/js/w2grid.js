$(function () {

    var sel ;

    var sdate;
    var scluster='*';

    $('#grid').w2grid({
        name: 'grid',
        header: 'List of Names',
        columns: [
            { field: 'cluster', caption: 'Cluster', size: '9%', sortable: true },
            { field: 'status', caption: 'Status', size: '13%', sortable: true },
            { field: 'run_start_time', caption: 'Run Start Time', size: '24%', sortable: true},
            { field: 'run_end_time', caption: 'Run End Time', size: '24%'},
            { field: 'run_secs', caption: 'Run Time(Sec)', size: '8%', sortable: true },
            { field: 'uid', caption: 'Unique ID', size: '22%', sortable: true },
        ],
        postData : {datefilter:sdate, cluster:$('#cluster').val()}

    });
    w2ui['grid'].load('/apiv1/tracer/tracergrid/');
    DrawChart();

    $("#style9").submit( function( event ){
      event.preventDefault();
      sdate =  $('#date').val();
      var url =  '/apiv1/tracer/tracergrid/' + sdate + '/' + scluster;
      w2ui['grid'].load(url);

      DrawChart();

    });

});
