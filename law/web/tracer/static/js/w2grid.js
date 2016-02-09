$().ready(function() {

    });

$(window).load(function () {

    var sel ;

    var processed;


    //var e = document.getElementById("datesel");
    //var tsvalue = e.options[e.selectedIndex].value;
    var tsvalue = $("#datesel").val();

    //startDt = '';
    if (!startDt){
       endDt = moment().format('YYYY-MM-DD HH:mm:ss');
       startDt = moment().subtract(1,'h').format('YYYY-MM-DD HH:mm:ss');
       if ($("#datesel").val() == 'custom'){
       $("#datesel").val('last1h');
       $("#dater").hide();
       var datetext = moment().format('YYYY-MM-DD HH:mm:ss').toString();
       $('#dater').data(datetext);
       $('#dater').data(datetext);

       }
    }
    period = $("#period").val();
    if (period == "" || !$.isNumeric(period)) {
      period = 30;
    }
    //e = document.getElementById("tstype");
    //tstype = e.options[e.selectedIndex].value;
    tstype = $("#tstype").val();
    var urlx = '/apiv1/tracer/tracergrid/';

    var isithot = $('#isithot').is(':checked');
    var PostData = JSON.parse(JSON.stringify(({'fdate':startDt,'tdate':endDt, 'cluster':$('#cluster').val(),'tstype':tsvalue,'isithot':isithot})))

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
            { field: 'run_start_time', caption: 'Run Start Time(PST)', size: '22%', sortable: true},
            { field: 'run_end_time', caption: 'Run End Time(PST)', size: '22%'},
            { field: 'run_secs', caption: 'Run Time(Sec)', size: '15%', sortable: true },
            { field: 'uid', caption: 'Unique ID', size: '19%', sortable: true },
        ],
        postData : PostData

    });
    /*if (processed != 'Y'){
        w2ui['grid'].load('/apiv1/tracer/tracergrid/');
    }*/


    DrawChart(period, tstype, tsvalue, isithot);

    $('#submit').click(function(event){
      event.preventDefault();
      processed = 'Y';
      //e = document.getElementById("datesel");
      //tsvalue = e.options[e.selectedIndex].value;
      tsvalue = $("#datesel").val();
      switch($( "#datesel" ).val()){
          case 'last1d':
             startDt = moment().subtract(1,'d').format('YYYY-MM-DD HH:mm:ss');
             endDt = moment().format('YYYY-MM-DD HH:mm:ss');
             break;

          case 'last1w':
             startDt = moment().subtract(1,'w').format('YYYY-MM-DD HH:mm:ss');
             endDt = moment().format('YYYY-MM-DD HH:mm:ss');
             break;

          case 'last1h':
             startDt = moment().subtract(1,'h').format('YYYY-MM-DD HH:mm:ss');
             endDt = moment().format('YYYY-MM-DD HH:mm:ss');
             break;
          default:
             break;

      };



      tstype = $("#tstype").val()


      period = $("#period").val();
      if (period == "" || !$.isNumeric(period)) {
         period = 30;
      }
      isithot = $('#isithot').is(':checked');
    if (isithot){
        document.getElementById("avrg").textContent="Percent Less Than 30 secs - All Clusters";
        document.getElementById("lt30").textContent="Percent where tracer was less than 30 seconds";
    }
    else
    {
        document.getElementById("avrg").textContent="Percent Less Than 2 secs - All Clusters";
        document.getElementById("lt30").textContent="Percent where tracer was less than 2 seconds";

    }
      PostData = JSON.parse(JSON.stringify(({'fdate':startDt,'tdate':endDt,
            'cluster':$('#cluster').val(),'tstype':tsvalue,'isithot':isithot})))


      var url =  '/apiv1/tracer/tracergrid/';
      w2ui['grid'].postData  = PostData;
      w2ui['grid'].reload();

      DrawChart(period, tstype, tsvalue, isithot);

    });

});
