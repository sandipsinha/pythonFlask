//
// Copyright:    Loggly, Inc.
// Author:       Scott Griffin
// Email:        scott@loggly.com
//
//
define( ['jquery', 'd3', 'nvd3'], function( $, d3, nv ) {
    var BarChart = function( selector, data, config ) {

        var utc_offset = new Date().getTimezoneOffset() * 60 * 1000 ;
        var _chart     = nv.models.multiBarChart()
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
//                           .color( ['#236B9E', '#9E5623'] ) ;
//                           .color( ['#E5975F', '#DA5FE4', '#69E45F', '#5FACE4'] );
        var _dataUrl   = config.dataUrl ;
        var _selector  = selector;
        var _bucketed  = 'quarter' ;
        var _start     = null;
        var _end       = null;

        if( config.timestamped ) {
            _chart.xAxis.tickFormat( function( d ) {
                return d3.time.format( '%Y-%m-%d' )(new Date(d + utc_offset ) ) ;
            });
        } 

        _chart.yAxis.tickFormat( function( d ) {
            return ' $' + d3.format( ',.2f' )( d ) ;
        });

        
        nv.utils.windowResize(_chart.update);
        nv.addGraph(function() { return _chart } ) ;

        if( config.timeBuckets ) {
            var namespace = _selector.split( ' ' )[0]
            var buttons = $( '<div align="center"></div>' )

            $( config.timeBuckets ).each( function( i, val ) {
                var html ;
                var ns_id = namespace + '_' + val ;
                html = '<input type="radio" data-bucket="' + val + '" id="' + ns_id + '" name="' + namespace + '">' +
                       '<label for="' + ns_id + '">' + val + '</label>' ;
                var node = $( html ) ;
                if( _bucketed === val ) {
                    node.attr( 'checked', 'checked' );
                }
                $( buttons ).append( node );
            });

            buttons.buttonset()

            // Bind the button selection
            buttons.insertAfter( selector ) ;
            $( buttons ).find( 'input' ).change( function() {
                _bucketed = $(this).data( 'bucket' ) ;
                updatePeriod( _start, _end, _bucketed ) ;
            });
        }

        if( config.dateSlider ) {

            // Set initial values based on the slider
            values = config.dateSlider.dateRangeSlider( 'values' ) ;
            _start = values.min.toISOString().split( 'T' )[0];
            _end   = values.max.toISOString().split( 'T' )[0];

            config.dateSlider.bind("valuesChanged", function(e, data){
                _start = data.values.min.toISOString().split( 'T' )[0];
                _end = data.values.max.toISOString().split( 'T' )[0];
                updatePeriod( _start, _end, _bucketed ) ;
            });
        }

        var updatePeriod = function( start, end, bucketby ) {
            params = $.param( {start:start, end:end, bucketed:bucketby} ) ;
            var url = _dataUrl + '?' + params;

            d3.json( url, function( error, json ) {
                if( error ) {
                    return;
                }
                d3.select( _selector )
                  .datum( json.series )
                  .call(_chart);
                _chart.update() ;
            });
        };
                
        if( data !== null ) {
            // Set the data for the chart and render
            _d3Obj = d3.select( selector )
                    .datum( data )
                    .call(_chart);
        } else if( config.dataUrl ) {
            // If no data was supplied then try to do the initial load from
            // the data url.
            updatePeriod( _start, _end, _bucketed ) ;
        } else {
            _d3Obj = d3.select( selector )
                    .datum( [] )
                    .call(_chart);
        }

   
        return {
            updatePeriod : updatePeriod,
            start        : _start,
            end          : _end,
            bucketed     : _bucketed,
        };
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


    return {
        BarChart: BarChart,
    }
});
