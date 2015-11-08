function createAverageChart(postData,dataGroup,postvarData, tsvalue ) {
  var vis = d3.select("#visualisation4")
    .attr("viewBox","30 0 730 690"),
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
    var avgamt = function(d) { return  d['average'] };
    var xScale = CreateTimeScale(postData);
    var yScale = CreateYScale(postData, avgamt);
    var lineGen = d3.svg.line()
      .x(function(d) {
        return xScale(parseDate(d.start_date));
      })
      .y(function(d) {
        return yScale(d['average']);
      }).interpolate("monotone")
      ;

    var color = d3.scale.category10();
    //color.domain(postDataKeys);

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
    .attr("y",  HEIGHT + MARGINS.bottom - 55   )
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

    AppendText(vis, "pcnt less than 30 secs - All Customers");
    vis.selectAll(".line").remove();
    vis.append('svg:path')
      .attr('d', lineGen(postvarData))
      .attr('stroke', 'green')
      .attr('stroke-width', 2)
      .attr("class","line")
      .attr('fill', 'none');

    vis.selectAll(".linePoint").remove();
    vis.selectAll(".linePoint")
       .data(postvarData)
       .enter().append("circle")
       .attr("class", "linePoint")
       .attr("cx", function (d,i) { return xScale(parseDate(d.start_date) ); })
       .attr("cy", function (d,i) { return yScale(d['average']); })
       .attr("r", "12")
       .style("fill", function (d,i) { return color(d.cluster); })
       .style("stroke", "grey")
       .style("stroke-width", "1px")
       .style('opacity', 1e-6)//1e-6
       .on("mouseover", function (d,i) { showPopover.call(this, d, 'avrg'); })
       .on("mouseout",  function (d,i) { removePopovers(); })


};

