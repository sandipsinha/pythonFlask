 function DrawChart(){
    $.ajax({
  			url : '/apiv1/tracer/tracerpercentile/',
  			contentType: "application/json",
  			dataType: "json",
  			type: "POST",
  			data: JSON.stringify({Date:$('#date').val(), Cluster:$('#cluster').val()}),
			success: function( data ) {
				  var processedData = JSON.parse(JSON.stringify(data));
				  createNintyFiveChart(processedData);
				  createNintyEightChart(processedData);

			}
  		});
}