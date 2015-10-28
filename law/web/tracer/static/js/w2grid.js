$(function () {

    var sel ;

    var processed;

    var e = document.getElementById("tstype");
    var tsvalue = e.options[e.selectedIndex].value;

    var PostData = JSON.parse(JSON.stringify(({'fdate':$('#fdate').val(),'tdate':$('#tdate').val(), 'cluster':$('#cluster').val(),'tstype':tsvalue})))

    $('#grid').w2grid({
        name: 'grid',
        header: 'List of Names',
        url: '/apiv1/tracer/tracergrid/',
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
            toolbarEdit    : false,
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
        postData : PostData

    });
    if (processed != 'Y'){
        w2ui['grid'].load();
    }

    DrawChart(tsvalue);

    $("#style9").submit( function( event ){
      event.preventDefault();
      processed = 'Y';
      tsvalue = e.options[e.selectedIndex].value;
      PostData = JSON.parse(JSON.stringify(({'fdate':$('#fdate').val(),'tdate':$('#tdate').val(),
            'cluster':$('#cluster').val(),'tstype':tsvalue})))


      var url =  '/apiv1/tracer/tracergrid/';
      w2ui['grid'].postData  = PostData;
      w2ui['grid'].reload();



      DrawChart(tsvalue);

    });

});
