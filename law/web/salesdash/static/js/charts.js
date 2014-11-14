//
// Copyright:    Loggly, Inc.
// Author:       Scott Griffin
// Email:        scott@loggly.com
//
//
define( ['jquery', 'd3', 'nvd3'], function( $, d3, nv ) {
    var barChart = function( selector, data, config ) {
        return nv.addGraph(function() {
            var utc_offset = new Date().getTimezoneOffset() * 60 * 1000 ;
            var chart = nv.models.multiBarChart()
                        .margin( {right:150} )
                        .x( function(d) { return d[0] })
                        .y( function(d) { return d[1] })
                        .rightAlignYAxis(true) 
                        .transitionDuration(150)
                        .reduceXTicks(true)
                        .rotateLabels(0)
                        .stacked( true )
                        .showControls(true)
                        .tooltips(true)
                        .groupSpacing(0.1) ;
//                        .color( ['#236B9E', '#9E5623'] ) ;
//                        .color( ['#E5975F', '#DA5FE4', '#69E45F', '#5FACE4'] );

            if( config.timestamped ) {
                chart.xAxis.tickFormat( function( d ) {
                    return d3.time.format( '%Y-%m-%d' )(new Date(d + utc_offset ) ) ;
                });
            } 

            chart.yAxis.tickFormat( function( d ) {
                return ' $' + d3.format( ',.2f' )( d ) ;
            });


            var d3Obj = d3.select( selector )
              .datum( data )
              .call(chart);
            
            // Bind the D3 data store to this chart object for easy updating
            chart.datum = function( data ) {
                d3Obj.datum( data );
                return chart
            }

            nv.utils.windowResize(chart.update);

            if( config.timeBuckets ) {
                var buttons = createTimeBucketing( config.timeBuckets ) ;
                buttons.insertAfter( selector ) ;
                start = '2014-04-08' ;
                end   = '2014-12-31' ;
                $( buttons ).find( 'input' ).change( function() {
                    updatePeriod( chart, config.dataUrl, start, end, $(this).data('bucket') ) ;
                });
            }

            if( config.dateSlider ) {
                config.dateSlider.bind("valuesChanged", function(e, data){
                    var start = data.values.min.toISOString().split( 'T' )[0];
                    var end = data.values.max.toISOString().split( 'T' )[0];
                    updatePeriod( chart, config.dataUrl, start, end, 'quarter' ) ;
                });
            }

            return chart ;
        });
    };

    var createTimeBucketing = function( buckets ) {
        var container = $( '<div id="bucket-control" align="center"></div>' )

        $( buckets ).each( function( i, val ) {
            $( container ).append( 
                $( '<input type="radio" data-bucket="' + val + '" id="' + val + '" name="project">' +
                   '<label for="' + val + '">' + val + '</label>' )
            );
        });

        container.buttonset()
        return container ;
    }

    var urlParams = function() {
        var params ;
        var paramList = window.location.search.slice( 1 ).split( '&' );
        for( var i = 0 ; i < paramList.length ; i++ ) {
            param = paramList[i].split( '=' );
            params[param[0]] = param[1];
        }
        
        return params
    }

    var updatePeriod = function( chart, dataUrl, start, end, bucketby ) {
        params = $.param( {start:start, end:end, bucketed:bucketby} ) ;
        var url = dataUrl + '?' + params;

        d3.json( url, function( error, json ) {
            if( error ) {
                return;
            }
            chart.datum(json.series).update() ;
        });
    };

    return {
        barChart: barChart,
        updatePeriod: updatePeriod
    }
});
