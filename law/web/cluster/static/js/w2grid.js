$(window).load(function () {


    //e = document.getElementById("tstype");
    //tstype = e.options[e.selectedIndex].value;
    clstrdata = $("#clstrdata").val();
    var urlx = '/apiv1/cluster/subdgrid/';


    var PostData = JSON.parse(JSON.stringify(({'cdata':clstrdata})))

    $('#grid').w2grid({
        name: 'grid',
        header: 'List of Subdomains',
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
            { field: 'subdomain', caption: 'Subdomain', size: '30%', sortable: true },
            { field: 'cid', caption: 'Customer ID', size: '35%', sortable: true },
            { field: 'acct_id', caption: 'Account ID', size: '35%', sortable: true},
            ],
        postData : PostData

    });
    w2ui['grid'].postData  = PostData;
    w2ui['grid'].load('/apiv1/cluster/subdgrid/');

    $('#clstrdata').change(function(event){
      event.preventDefault();
      clstrdata = $("#clstrdata").val();
      PostData = JSON.parse(JSON.stringify(({'cdata':clstrdata})))

      url =  '/apiv1/cluster/subdgrid/';
      w2ui['grid'].postData  = PostData;
      w2ui['grid'].load('/apiv1/cluster/subdgrid/');

    });

});
