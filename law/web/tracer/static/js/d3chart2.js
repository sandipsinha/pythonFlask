function createNintyNineChart(postData,dataGroup, postDataKeys, postDataValues, postvarData, tsvalue ) {


    var vis = d3.select("#visualisation3"),
    WIDTH = window.GWIDTH,
    HEIGHT = window.GHEIGHT,
    PADDING = window.GPADDING,
    MARGINS = {
        top: window.GTOP,
        right: window.GRIGHT,
        bottom: window.GBOTTOM,
        left: window.GLEFT
    };

    var format = d3.time.format("%Y-%m-%d");
    //var dateFN = function(d) { return format.parse(d['start_date']) };


    var ninty_nine = function(d) { return d['99th_perc'] };

    var xScale = CreateTimeScale(postData);


    var yScale = CreateYScale(postData, ninty_nine)

    //defines a function to be used to append the title to the tooltip.  you can set how you want it to display here.

    var line = d3.svg.line()
          .interpolate("basis")
          .x(function (d) { return x(parseDate(d['start_date'])) })
          .y(function (d) { return y(d['99th_perc']); });

    var color = d3.scale.category10();
    color.domain(postDataKeys);

    xAxis = formatXaxis(xScale, tsvalue);

    yAxis = d3.svg.axis()
            .scale(yScale)
            .orient("left");

     if (vis.selectAll(".xaxis")[0].length < 1 ){
        vis.append("g")
        .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom - MARGINS.top - 69 ) + ")")
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
    .attr("y",  HEIGHT + MARGINS.bottom -55  )
    .style("text-anchor", "middle")
    .style("font-weight", 'bold')
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



    var color = LineColors();
    AppendText(vis, "99th Percentile secs");

    vis.selectAll(".legend").remove();

    var legend = vis.selectAll(".legend")
            .data(postDataKeys)
            .enter().append("g")
            .attr("class", "legend")
            .attr("transform", function (d, i) { return "translate(38," + i * 20 + ")"; });


    legend.append("rect")
        .attr("x", WIDTH - 56)
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
        return yScale(d['99th_perc']);
      }).interpolate("monotone");

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
    vis.selectAll(".linePoint").remove();
    vis.selectAll(".linePoint")
       .data(postvarData)
       .enter().append("circle")
       .attr("class", "linePoint")
       .attr("cx", function (d,i) { return xScale(parseDate(d.start_date) ); })
       .attr("cy", function (d,i) { return yScale(d['99th_perc']); })
       .attr("r", "12")
       .style("fill", function (d,i) { return color(d.cluster); })
       .style("stroke", "grey")
       .style("stroke-width", "1px")
       .style('opacity', 1e-6)//1e-6
       .on("mouseover", function (d,i) { showPopover.call(this, d, '99'); })
       .on("mouseout",  function (d,i) { removePopovers(); })


};

