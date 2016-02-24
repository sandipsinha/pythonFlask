 function DrawChart(period, tstype, griddt, isithot){

    $.ajax({
  			url : '/apiv1/tracer/traceraverage/',
  			contentType: "application/json",
  			dataType: "json",
  			type: "POST",
  			data: JSON.stringify({tdate:endDt, dateind: tstype,periods:period,'isithot':isithot}),
			success: function( data ) {
				  var processedData = JSON.parse(JSON.stringify(data));
				  var dataGroup = processedData;
                  var postvarData = dataGroup;

				  createAverageChart(processedData,dataGroup, postvarData,tstype,isithot);

			}
  		});


    $.ajax({
  			url : '/apiv1/tracer/tracerpercentile/',
  			contentType: "application/json",
  			dataType: "json",
  			type: "POST",
  			data: JSON.stringify({Cluster:$('#cluster').val(),tdate:endDt, griddateval: griddt, dateind: tstype,periods:period,'isithot':isithot}),
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

				  createNintyFiveChart(processedData,dataGroup, postDataKeys, postDataValues , postvarData,tstype);
				  createNintyEightChart(processedData,dataGroup, postDataKeys, postDataValues , postvarData,tstype);
				  createNintyNineChart(processedData,dataGroup, postDataKeys, postDataValues , postvarData,tstype);
				  createLessThan30Chart(processedData,dataGroup, postDataKeys, postDataValues , postvarData,tstype, isithot);

			}
  		});
}