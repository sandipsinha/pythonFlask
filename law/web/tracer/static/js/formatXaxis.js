 function formatXaxis(xScale, tsvalue){
  switch(tsvalue) {
        case 'd' :
            return xAxis = d3.svg.axis()
                   .scale(xScale)
                   .ticks(d3.time.day, 5)
                   .tickFormat(d3.time.format('%b %d'))
                   .tickPadding(5)
                   .orient("bottom");
            break;
        case 'w':
            return xAxis = d3.svg.axis()
                   .scale(xScale)
                   .ticks(d3.time.week, 2)
                   .tickFormat(d3.time.format('%b %d'))
                   .tickPadding(5)
                   .orient("bottom");
                   break;
        case 'm':
            return xAxis = d3.svg.axis()
                   .scale(xScale)
                   .ticks(d3.time.month, 1)
                   .tickFormat(d3.time.format('%B'))
                   .tickPadding(5)
                   .orient("bottom");
                   break;
           }
}