 function DrawChart(tsvalue){
    $.ajax({
  			url : '/apiv1/tracer/tracerpercentile/',
  			contentType: "application/json",
  			dataType: "json",
  			type: "POST",
  			data: JSON.stringify({fdate:$('#fdate').val(), Cluster:$('#cluster').val(),tdate:$('#tdate').val(), tstype: tsvalue}),
			success: function( data ) {
				  var processedData = JSON.parse(JSON.stringify(data));
				  var dataGroup = d3.nest()
                    .key(function(d) {
                        return d['cluster']
                  })
                  .entries(processedData);
                  var postDataKeys = [];
                  var postDataValues = [];
                  for(i in dataGroup){

                  var key = dataGroup[i].key;
                  var val = dataGroup[i].values;
                  postDataValues.push(val);
                  for(j in val){

                        var sub_key = j;
                        var sub_val = val[j];
                  }

                  postDataKeys.push(key);
                  }
                  var postvarData = _.flatten(postDataValues);

				  createNintyFiveChart(processedData,dataGroup, postDataKeys, postDataValues , postvarData);
				  createNintyEightChart(processedData,dataGroup, postDataKeys, postDataValues , postvarData);
				  createNintyNineChart(processedData,dataGroup, postDataKeys, postDataValues , postvarData);

			}
  		});
}