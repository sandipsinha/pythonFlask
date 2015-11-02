$(function() {

    function cb(start, end) {
        $('#dater span').html(start.format('YYYY-MM-DDThh:mm:ss') + ' - ' + end.format('YYYY-MM-DDThh:mm:ss'));
    }
    cb(moment().subtract(1, 'h'), moment());

    $('#dater').daterangepicker({
        "timePicker":true,
        "timePicker24Hour":true,
        "autoApply":true,
        "locale": {
            format: 'MM/DD/YYYY h:mm A'
        }
        }, cb);
      if ($("#datesel").val() == 'custom'){
      $('.cstm').show();
      }
      else{
      $('.cstm').hide();
      }
     $( "#datesel" ).change(function() {
     if ($("#datesel").val() == 'custom'){
      $('.cstm').show();
      }
      else{
      $('.cstm').hide();

      switch ($("#datesel").val()){
      case 'last1h':
        endDt = moment().format('YYYY-MM-DD HH:mm:ss');
        startDt = moment().subtract(1,'h').format('YYYY-MM-DD HH:mm:ss');
        break;
      case 'last1d':
        endDt = moment().format('YYYY-MM-DD HH:mm:ss');
        startDt = moment().subtract(1,'d').format('YYYY-MM-DD HH:mm:ss');
        break;
      case 'last1w':
        endDt = moment().format('YYYY-MM-DD HH:mm:ss');
        startDt = moment().subtract(1,'w').format('YYYY-MM-DD HH:mm:ss');
        break;
      default:
        break;
      }

      }
    });
    $("#dater").on('apply.daterangepicker',function(ev, picker){

     startDt = picker.startDate.format('YYYY-MM-DD HH:mm:ss');

     endDt = picker.endDate.format('YYYY-MM-DD HH:mm:ss');
    });

});