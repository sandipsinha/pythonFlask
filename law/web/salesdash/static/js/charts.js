//
// Copyright:    Loggly, Inc.
// Author:       Scott Griffin
// Email:        scott@loggly.com
//
//
define( ['jquery', 'd3', 'nvd3', 'underscore'], function( $, d3, nv, _ ) {
    var Chart = function( selector, data, config ) {
       
        var OVERRIDE_TICKS_TYPES = ['area', 'barAndLine' ];

        var utc_offset = new Date().getTimezoneOffset() * 60 * 1000 ;
        var _chart     = null ;
        var _config    = config ;
        var _dataUrl   = config.dataUrl ;
        var _selector  = selector;
        var _bucketed  = 'quarter' ;
        var _d3Obj     = null ;
        var _start     = null;
        var _end       = null;
        
        if( config.type === undefined || config.type === 'bar' ) {
            _chart = nv.models.multiBarChart()
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
        //             .color( ['#236B9E', '#9E5623'] ) ;
        //             .color( ['#E5975F', '#DA5FE4', '#69E45F', '#5FACE4'] );

            _chart.yAxis.tickFormat( function( d ) {
                return ' $' + d3.format( ',.2f' )( d ) ;
            });
        } else if( config.type === 'area' ) {
            _chart = nv.models.stackedAreaChart()
                    .margin( {right:150} )
                    .x( function(d) { return d.x })
                    .y( function(d) { return d.y })
                    .rightAlignYAxis(true) 
                    .transitionDuration(150)
                    .showControls(true)
                    .controlsData( ['Stacked', 'Expanded'] )
                    .tooltips(true)
                    .useInteractiveGuideline( true )
                    .clipEdge( true ); 
            
            _chart.yAxis.tickFormat( function( d ) {
                return d3.format( 'd' )( d ) ;
            });
        } else if( config.type === 'barAndLine' ) {
            _chart = nv.models.linePlusBarChart()
                    .margin( {right:150} )
                    .x( function(d) { return d.x })
                    .y( function(d) { return d.y });
//                    .showControls(true)
//                    .tooltips(true)
//                    .clipEdge( true ); 
            _chart.y1Axis.tickFormat( function( d ) {
                return d3.format( 'd' )( d ) ;
            });
            _chart.y2Axis.tickFormat( function( d ) {
                return d3.format( ',.2%' )( d ) ;
            });
        }


        if( config.timestamped ) {
            chart.xAxis.tickFormat( function( d ) {
                return d3.time.format( '%Y-%m-%d' )(new Date(d + utc_offset ) ) ;
            });
        } 

        
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

        // This is needed to force the tick values for specific graph types.
        var overrideTicks = function(data) {
            if( _config && OVERRIDE_TICKS_TYPES.indexOf( _config.type ) != -1 ) {
                _chart.xAxis
                    .ticks( data[0].labels.length )
                    .tickFormat( function( d ) {
                        return data[0].labels[d];
                    });
            }
        };

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
                
                // Line style charts need to have our strings based ticks forced
                // into a specific format.
                overrideTicks(json.series);
                _chart.update() ;
            });
        };
                
        if( data !== null ) {
            // Set the data for the chart and render
            overrideTicks( data ) ;
            _d3Obj = d3.select( selector )
                    .datum( data )
                    .call(_chart);
            _chart.update()
        } else if( config.dataUrl ) {
            // If no data was supplied then try to do the initial load from
            // the data url.
            updatePeriod( _start, _end, _bucketed ) ;
        } else {
            _d3Obj = d3.select( selector )
                    .datum( [] )
                    .call(_chart);
            _chart.update()
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
        BarChart        : function( selector, data, config ) { config.type='bar'; return Chart( selector, data, config) },
        AreaChart       : function( selector, data, config ) { config.type='area'; return Chart( selector, data, config) },
        LineAndBarChart : function( selector, data, config ) { config.type='barAndLine'; return Chart( selector, data, config) },
    }
});
