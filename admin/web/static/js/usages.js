var UsagesManager = {
    initialize: function(){
        UsagesManager.initializeChart();
    },
    
    update: function(response){
        UsagesManager.updateChart(response.usages);
    },
    
    initializeChart: function(){
        var chartId = '#user-usages-chart svg';
        var chart;
        nv.addGraph(function(data){
            chart = nv.models.multiBarChart()
                .x(function(d){return new Date(d.datetime*1000);})
                .y(function(d){return d.count;})
                .color(d3.scale.category10().range());
            chart.xAxis
                .axisLabel('Time')
                .showMaxMin(false)
                .tickFormat(function(d){return d3.time.format('%x')(new Date(d));});
            chart.yAxis
                .tickFormat(d3.format(',.0f'));                
            nv.utils.windowResize(chart.update);
            return chart;
        });
        $(chartId).height(300);
        
        UsagesManager.updateChart = function(data){
            d3.select(chartId)
                .datum(data)
                .transition().duration(500).call(chart);
        }
    }
};

var UsagesRequestor = {
    getUsages: function(uri){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'GET',
            dataType:'json',
            success:UsagesManager.update
        });
    }
};

$(document).ready(function(){
    UsagesManager.initialize();
});