


function createNintyFiveChart(postData) {

    var dataGroup = d3.nest()
    .key(function(d) {
        return d['cluster']
    })
    .entries(postData);

    //var dataGroups = JSON.parse(JSON.stringify(dataGroup))
    var vis = d3.select("#visualisation"),
    WIDTH = 680,
    HEIGHT = 500,
    PADDING = 100,
    MARGINS = {
        top: 20,
        right: 20,
        bottom: 20,
        left: 100
    };
    var postDataKeys = [];
    for(i in dataGroup){

    var key = dataGroup[i].key;
    var val = dataGroup[i].values;
    for(j in val){

        var sub_key = j;
        var sub_val = val[j];
        //console.log(JSON.parse(JSON.stringify(sub_val)));

    }

    postDataKeys.push(key)
}



    var format = d3.time.format("%Y-%m-%d");
    //var dateFN = function(d) { return format.parse(d['start_date']) };

    var parseDate = d3.time.format("%Y-%m-%d").parse;


    var ninty_eight = function(d) { return d['95th_perc'] };


    var xScale = d3.time.scale()
                     .range([MARGINS.left+ 5, WIDTH - MARGINS.right - MARGINS.left])
                     .domain(d3.extent(postData, function(d) { return parseDate(d.start_date); }));

    var yScale = d3.scale.linear()
                     .range([HEIGHT - MARGINS.top, MARGINS.bottom])
                     .domain(d3.extent(postData, ninty_eight));

    //defines a function to be used to append the title to the tooltip.  you can set how you want it to display here.

    var line = d3.svg.line()
          .interpolate("basis")
          .x(function (d) { return x(parseDate(d['start_date'])) })
          .y(function (d) { return y(d['95th_perc']); });

    var color = d3.scale.category10();
    color.domain(postDataKeys);

    xAxis = d3.svg.axis()
           .scale(xScale)
           .ticks(d3.time.day, 1)
           .tickFormat(d3.time.format('%b %d'))
           .tickPadding(5)
           .orient("bottom");

    yAxis = d3.svg.axis()
            .scale(yScale)
            .orient("left");

     if (vis.selectAll(".xaxis")[0].length < 1 ){
        vis.append("g")
        .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
        .attr("class","xaxis")
       .call(xAxis)
       .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)" );
        // otherwise, update the axis
        } else {
          vis.selectAll(".xaxis").transition().duration(1500).call(xAxis).selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)" );
        }


    vis.append("text")      // text label for the x axis
    .attr("x", WIDTH/2 - MARGINS.right +30)
    .attr("y",  HEIGHT + MARGINS.bottom + MARGINS.top + 7 )
    .style("text-anchor", "middle")
    .text("Date");

    if (vis.selectAll(".yaxis")[0].length < 1 ){
        vis.append("g")
        .attr("transform", "translate(" + (MARGINS.left) + ",0)")
        .attr("class","yaxis")
       .call(yAxis)
        // otherwise, update the axis
        } else {
          vis.selectAll(".yaxis").transition().duration(1500).call(yAxis)
        }

    vis.append("text")
        .attr("x", (WIDTH / 2))
        .attr("y", (MARGINS.top))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("text-decoration", "underline")
        .style("font-weight", "bold")
        .text("Ninty Five Percentile");

    var color = d3.scale.ordinal()
      .range(["#0000FF","#FF00FF","#00FF00","#FFFF00","#00FFFF","#845B47","#0080FF","#FF8000","#F4A460","#FFDEAD", "#D2691E","#C71585","#800080","#48D1CC","#006400","#B8860B","#FF4500","#FF6347"]);

    vis.append("text")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("transform", "translate("+ (PADDING/2) +","+(HEIGHT/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
            .text("95th Percentile");

    vis.selectAll(".legend").remove();
    var legend = vis.selectAll(".legend")
            .data(postDataKeys)
            .enter().append("g")
            .attr("class", "legend")
            .attr("transform", function (d, i) { return "translate(55," + i * 20 + ")"; });

    legend.append("rect")
        .attr("x", WIDTH - 62)
        .attr("y", function(d, i){ return i *  15;})
        .attr("width", 10)
        .attr("height", 10)
        .style("stroke", "grey")
        .style("fill", function(d, i) {
         return color(postDataKeys[i]);
      });

    legend.append("text")
        .attr("x", WIDTH - 80)
        .attr("y", function(d, i){ return i *  15 + 7 ;})
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function (d) { return d; });


    var lineGen = d3.svg.line()
      .x(function(d) {
        return xScale(parseDate(d.start_date));
      })
      .y(function(d) {
        return yScale(d['95th_perc']);
      }).interpolate("basis");

     vis.selectAll(".line").remove();
     dataGroup.forEach(function(d, i) {
        vis.append('svg:path')
        .data(dataGroup)
        .attr('d', lineGen(d['values']))
         .attr("stroke", function(d) {return color(postDataKeys[i]); })
        .attr('stroke-width', 2)
        .transition().duration(1500)
        .attr("class","line")
        .attr('fill', 'none');

      });
};

