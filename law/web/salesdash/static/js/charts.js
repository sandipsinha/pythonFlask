//
// Copyright:    Loggly, Inc.
// Author:       Scott Griffin
// Email:        scott@loggly.com
//
//
define( ['d3', 'nvd3'], function( d3, nv ) {
    var barChart = function( selector, data, timestamped ) {
            return nv.addGraph(function() {
            var utc_offset = new Date().getTimezoneOffset() * 60 * 1000 ;
            var chart = nv.models.multiBarChart()
                        .margin( {right:150} )
                        .x( function(d) { return d[0] })
                        .y( function(d) { return d[1] })
                        .rightAlignYAxis(true) 
                        .transitionDuration(350)
                        .reduceXTicks(true)
                        .rotateLabels(0)
                        .showControls(true)
                        .tooltips(true)
                        .groupSpacing(0.1) ;
//                        .color( ['#236B9E', '#9E5623'] ) ;
//                        .color( ['#E5975F', '#DA5FE4', '#69E45F', '#5FACE4'] );

            if( timestamped ) {
                chart.xAxis.tickFormat( function( d ) {
                    return d3.time.format( '%Y-%m-%d' )(new Date(d + utc_offset ) ) ;
                });
            } 

            chart.yAxis.tickFormat( function( d ) {
                return ' $' + d3.format( ',.2f' )( d ) ;
            });

//            chart.tooltip( function( key, x, y, e, chart ) {
//                return key + chart.yAxis.tickFormat()( e.value ) ;
//            }) ;

            d3.select( selector )
                .datum( data )
                .call(chart);

            nv.utils.windowResize(chart.update);

            return chart;
        });
    } ;


    return {
        barChart: barChart,
    }
});
