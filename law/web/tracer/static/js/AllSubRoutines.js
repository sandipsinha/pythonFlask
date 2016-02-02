 var parseDate = d3.time.format("%Y-%m-%d").parse;

function LineColors(){

    return d3.scale.ordinal()
      .range(["#0000FF","#FF00FF","#00FF00","#FFFF00","#00FFFF","#845B47","#0080FF","#FF8000","#F4A460","#FFDEAD", "#D2691E","#C71585","#800080","#48D1CC","#006400","#B8860B","#FF4500","#FF6347"]);

  }

function AppendText(vis, texts ){
return vis.append("text")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("transform", "translate("+ (window.GPADDING/2  ) +","+(window.GHEIGHT/2 - 25)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
            .attr("class","strong")
            .text(texts);
}

function CreateTimeScale(datas){
   return d3.time.scale()
                     .range([window.GLEFT , window.GWIDTH - window.GRIGHT - window.GLEFT + 50])
                     .domain(d3.extent(datas, function(d) { return parseDate(d.start_date); }))
                     ;
}

function CreateYScale(datas, values){
   return d3.scale.linear()
                     .range([window.GHEIGHT - window.GTOP - window.GBOTTOM-67, window.GBOTTOM])
                     .domain(d3.extent(datas, values));
                     }



function removePopovers () {
          $('.popover').each(function() {
            $(this).remove();
          });
        }

function showPopover (d, charttype, isithot) {
          var popuptext = '';
          switch (charttype){
          case '95':
            popuptext =  "<br/>95th Percentile: " + d['95th_perc'] ;
            break;
          case '98':
            popuptext =  "<br/>98th Percentile: " + d['98th_perc'] ;
            break;
          case '99':
            popuptext =  "<br/>99th Percentile: " + d['99th_perc'] ;
            break;
          case 'pcnt':
            if (isithot){
                  popuptext =  "<br/>Percentage LT 30: " + d['pcnt_LT30'] ;
                  }
                else{
                  popuptext =  "<br/>Percentage LT 2: " + d['pcnt_LT30'] ;
                }

            break;
          case 'avrg':
            if (isithot){
                    popuptext =  "<br/>Percentage LT 30(All Clusters): " + d['average'] ;
                    }
                  else{
                    popuptext =  "<br/>Percentage LT 2(All Clusters): " + d['average'] ;
                    }

            break;
          }
          $(this).popover({
            title: d.cluster,
            container: 'body',
            placement: 'auto top',
            trigger: 'manual',
            html : true,
            content: function() {
              return "Date: " + d.start_date +
                     popuptext; }
                      });
          $(this).popover('show')
       }

// returns slope, intercept and r-square of the line
function leastSquares(xSeries, ySeries) {
		var reduceSumFunc = function(prev, cur) { return prev + cur; };

		var xBar = xSeries.reduce(reduceSumFunc) * 1.0 / xSeries.length;
		var yBar = ySeries.reduce(reduceSumFunc) * 1.0 / ySeries.length;

		var ssXX = xSeries.map(function(d) { return Math.pow(d - xBar, 2); })
			.reduce(reduceSumFunc);

		var ssYY = ySeries.map(function(d) { return Math.pow(d - yBar, 2); })
			.reduce(reduceSumFunc);

		var ssXY = xSeries.map(function(d, i) { return (d - xBar) * (ySeries[i] - yBar); })
			.reduce(reduceSumFunc);

		var slope = ssXY / ssXX;
		var intercept = yBar - (xBar * slope);
		var rSquare = Math.pow(ssXY, 2) / (ssXX * ssYY);

		return [slope, intercept, rSquare];
	}