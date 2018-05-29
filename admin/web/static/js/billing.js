var BillingManager = {
    calculateBills: function(response){
        if(!response.consumptions)return;
        var plan = BillingManager.getPlan();
        plan = BillingPlans.getPlan(plan);
        var bills = response.consumptions.map(function(consumption){
            var date = d3.time.format('%b %Y')(new Date(consumption.datetime*1000));
            var count = consumption.count;
            var overage = (count > plan.limit) ? (count - plan.limit) : 0.0
            var surcharge = Math.round(overage * plan.overage * 100) / 100;
            var total = plan.monthly + surcharge;
            var data = [date, count, overage, surcharge, total];
            return '<tr><td>'+data.join('</td><td>')+'</td></tr>';
        }).join('');
        $('#users-billing-tbody').html(bills);
    },
    
    getPlan: function(){
        return {
            monthly: parseFloat($('#user-plan-monthly').val()),
            limit: parseFloat($('#user-plan-limit').val()),
            overage: parseFloat($('#user-plan-overage').val())
        };
    }
};

var BillingRequestor = {
    getConsumptions: function(uri){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'GET',
            dataType:'json',
            success:BillingManager.calculateBills
        });
    }
};

var BillingPlans = {
    getPlan: function(plan){
        if(!plan) return BillingPlans.basic;
        if(plan.monthly || plan.limit || plan.overage) return plan;
        if(plan.name) return BillingPlans.getPlan(BillingPlans[plan.name]);
        return BillingPlans.basic;
    },
    
    trial: {
        monthly: 0,
        limit: 0,
        overage: 0.05
    },
    
    basic: {
        monthly: 500,
        limit: 10000,
        overage: 0.05
    },
    
    pro: {
        monthly: 2500,
        limit: 100000,
        overage: 0.025
    },
    
    enterprise: {
        monthly: 10000,
        limit: 1000000,
        overage: 0.01
    }
};

$(document).ready(function(){
});