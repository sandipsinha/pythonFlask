//
// Copyright:    Loggly, Inc.
// Author:       Scott Griffin
// Email:        scott@loggly.com
//
//

require.config({
    paths: {
        nvd3      : 'nv.d3.min',
        d3        : 'd3.v3.min',
        jquery    : '//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min',
        jquery_ui : '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min',
        jqsliders : 'jQRangeSlider-5.7.0/jQAllRangeSliders-withRuler-min'
    },
    shim: {
        nvd3 : {
            deps: ['d3'],
            exports: 'nv'
        },
        jquery_ui : {
            deps: ['jquery'],
            exports: '$'
        },
        jqsliders : {
            deps: ['jquery_ui'],
        }
    }
}) ;

