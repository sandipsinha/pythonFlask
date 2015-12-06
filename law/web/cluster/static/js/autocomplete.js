$(function() {

var p = $("#subd").val();

$('.subd').autocomplete({
	source: function( request, response ) {
  		$.ajax({
  			url : '/apiv1/cluster/getsubds',
  			dataType: "json",
  			data: {term:$("#subd").val()},
            success: function( data ) {
				 response( $.map( data, function( item ) {
				 	var code = item;
				 	$("#cluster").val(' ');
				    $("#cid").val(' ');
				    $("#acctid").val(' ');
				 	return {
						label: code,
						value: code,
						data : item
					}

				}));
			}
  		});
  	},
  	minLength: 0,
    select: function( event, ui ) {
		var names = ui.item.data;
		$.ajax({
  			url : '/apiv1/cluster/getclstrdtls',
  			dataType: "json",
  			data: {term:names},
            success: function( data ) {
                 var objar = data.split('|');
				 $("#cluster").val(objar[0]);
				 $("#cid").val(objar[1]);
				 $("#acctid").val(objar[2]);


			}
  		});
    }
}).bind('click', function(){ $(this).autocomplete("search"); } );


});

