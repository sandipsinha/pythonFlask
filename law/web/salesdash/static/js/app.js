//
// Copyright:    Loggly, Inc.
// Author:       Scott Griffin
// Email:        scott@loggly.com
//
//

require.config({
    shim: {
        nvd3 : {
            deps: ['d3'],
            exports: 'nv'
        }
    },
    paths: {
        nvd3   : 'nv.d3.min',
        d3     : 'd3.v3.min',
        jquery : '//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js',
    }
}) ;

