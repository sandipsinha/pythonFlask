//
// Copyright:    Loggly, Inc.
// Author:       Scott Griffin
// Email:        scott@loggly.com
//
//
define( [ 'jquery', 'jquery_ui',  'jqsliders', 'charts' ], function( $, $ui, jqsliders, charts ) {

    var dateSlider = function( id, start, end ) {
        var start_utc = new Date( 2013, 8, 1 ) ;
        var end_utc = new Date( end.split( '-' ) ) ;
        var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"];

        var node = $(id );
        node.dateRangeSlider({
            bounds: { 
                min: start_utc, 
                max: end_utc 
            },
            defaultValues: { 
                min: new Date( start.split( '-' ) ), 
                max: new Date( end.split( '-' ) ) 
            },
            scales: [{
                first: function(value){ return value; },
                end: function(value) {return value; },
                next: function(value){
                    var next = new Date(value);
                    return new Date(next.setMonth(value.getMonth() + 1));
                },
                label: function(value){
                    return months[value.getMonth()] + ' ' + value.getFullYear() ;
                },
//                format: function(tickContainer, tickStart, tickEnd){
//                    tickContainer.addClass("myCustomClass");
//                }
                }],
            valueLabels: "change"
        });

        return node;
    }

    return {
        dateSlider: dateSlider,
    }
});
