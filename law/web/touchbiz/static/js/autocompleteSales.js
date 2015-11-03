$(function (){

$('#rep_name').autocomplete({
	source: function( request, response ) {
  		$.ajax({
  			url : '/apiv1/touchbiz/salesrepid',
  			dataType: "json",
  			data: {term:$('#rep_name').val()},
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
		$('#rep_name').val(names[0]);
		$('#sales_rep_id').val(names[2]);

	}
});

})