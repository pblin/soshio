var SubscriptionsManager = {
    populateSubscriptionsList: function(uri, response){
        $('#user-subscriptions-button').attr('data-uri',uri);
        console.log(response);
        if(response.current){
            var rows = response.current.map(function(subscription){
                var row = '<li><p><a href="javascript:SubscriptionsManager.populateSubscription(\''+subscription.query+'\',\''+(subscription.description||'')+'\',\''+(subscription.tags||'')+'\');">'+subscription.query+'</a> <small class="muted">'+SubscriptionsManager.getMonthDayYearString(subscription.datetime)+'</small> <a href="javascript:SubscriptionsRequestor.removeSubscription(\''+uri+'/'+subscription.query+'\');"><i class="icon-remove-sign"></i></a>';
                if(subscription.description) row += '<br/><small class="muted">'+subscription.description+'</small>';
		if(subscription.tags) row += '<br/><small class="muted"><i class="icon-tags"></i>  '+subscription.tags+'</small>';
                row += '</p></li>';
                return row;
            }).join('');
            $('#user-subscriptions-list').html(rows);
        }
        if(response.past){
            var rows = response.past.map(function(subscription){
                return '<li><p>'+subscription.query+' <a href="javascript:updateQuery(\''+subscription.query+'\');"><i class="icon-plus-sign"></i></a></p></li>';
            }).join('');
            $('#user-past-subscriptions-list').html(rows);
        }
    },
    
    populateSubscription: function(query, description, tags){
        $('#user-subscriptions-query').val(query);
        $('#user-subscriptions-description').val(description); 
        $('#user-subscriptions-tags').val(tags); 
    },
    
    updateSubscription: function(element){
        var uri = $(element).attr('data-uri');
        var query = $('#user-subscriptions-query').val();
        var data = $('#user-subscriptions-form').serialize();
        SubscriptionsRequestor.updateSubscription(uri, query, data);
    },
    
    getMonthDayYearString: function(timestamp){
        var date = new Date(timestamp*1000);
        return (date.getMonth()+1)+'/'+date.getDate()+'/'+date.getFullYear();
    }
};

var SubscriptionsRequestor = {
    getSubscriptions: function(uri){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'GET',
            dataType:'json',
            success: function(response){
                SubscriptionsManager.populateSubscriptionsList(uri, response);
            }
        });
    },
    
    removeSubscriptions: function(uri){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'DELETE',
            dataType:'json'
        });
    },
    
    removeSubscription: function(uri){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'DELETE',
            dataType:'json',
            success: function(response){
                SubscriptionsRequestor.getSubscriptions(response.index_uri);
            }
        });
    },
    
    updateSubscription: function(uri, query, data){
        $.ajax({
            url:encodeURIComponent(uri+'/'+query),
            type:'POST',
            data:data,
            dataType:'json',
            success: function(response){
                SubscriptionsRequestor.getSubscriptions(uri);
            }
        });
    }
};

$(document).ready(function(){
});