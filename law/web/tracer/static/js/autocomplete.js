$(function() {

$('#cluster').autocomplete({
	source: function( request, response ) {
  		$.ajax({
  			url : '/apiv1/tracer/getclusters',
  			dataType: "json",
  			data: {term:$('#cluster').val()},
			success: function( data ) {
				 response( $.map( data, function( item ) {
				 	var code = item.split("|");
				 	return {
						label: code[0],
						value: code[1],
						data : item
					}

				}));
			}
  		});
  	},
  	autoFocus: true,
  	minLength: 2,
    select: function( event, ui ) {
		var names = ui.item.data.split("|");
		$('#cluster').val(names[1]);
    }
});


});

