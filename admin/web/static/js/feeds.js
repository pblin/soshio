var FeedsManager = {
    initialize: function(minutes){
        FeedsManager.initializeChart();
        minutes = minutes || 60;
        window.setInterval(FeedRequestor.getFeeds, minutes * 60 * 1000);
    },
    
    update: function(response){
        console.log(response);
        FeedsManager.updateChart(response.throughput);
    },
    
    initializeChart: function(){
        var chartId = '#environment-feeds-chart svg';
        var chart;
        nv.addGraph(function(data){
            chart = nv.models.stackedAreaChart()
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
        $(chartId).height(500);
        
        FeedsManager.updateChart = function(data){
            d3.select(chartId)
                .datum(data)
                .transition().duration(500).call(chart);
        }
    }
};

var FeedRequestor = {
    getFeeds: function(){
        $.ajax({
            url:encodeURIComponent('/services/feeds'),
            type:'GET',
            dataType:'json',
            success:FeedsManager.update
        });
    }
};

$(document).ready(function(){
    FeedsManager.initialize();
    FeedRequestor.getFeeds();
});