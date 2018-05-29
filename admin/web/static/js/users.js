var UsersManager = {
    initialize: function(){
        UsersRequestor.getUsers();
    },
    
    setPlan: function(name){
        $('#user-plan-name').val(name);
        var plan = BillingPlans[name];
        $('#user-plan-monthly').val(plan.monthly);
        $('#user-plan-limit').val(plan.limit);
        $('#user-plan-overage').val(plan.overage);
    },
    
    populateUsersTable: function(response){
        var rows = response.users.map(function(user){
            var data = [
                '<button class="btn btn-link" onclick="UsersRequestor.getUser(\''+user.uri+'\');">'+user.username+'</button>',
                new Date(user.datetime*1000).toString(),
                user.plan,
                user.disabled ?
                    '<span class="label label-warning"><i class="icon icon-time icon-white"></i></span>' :
                    '<span class="label label-success"><i class="icon icon-signal icon-white"></i></span>',
                UsersManager.getManageButtons(user.uri)
            ];
            return '<tr><td>'+data.join('</td><td>')+'</td></tr>';
        });
        $('#users-tbody').html(rows.join(''));
    },
    
    getManageButtons: function(uri){
        return '<div class="btn-group">' +
            '<button class="btn btn-success" onclick="UsersRequestor.manageUser(\''+uri+'\',\'enable\');return false;">Enable</button>' +
            '<button class="btn btn-warning" onclick="UsersRequestor.manageUser(\''+uri+'\',\'disable\');return false;">Disable</button>' +
            '<button class="btn btn-danger" onclick="UsersRequestor.removeUser(\''+uri+'\');return false;">Remove</button>' +
            '</div>';
    },
    
    populateUserModal: function(uri, response){
        $('#user-modal form .form-actions').show();
        $('#user-modal-username').hide();
        $('#user-modal-add-button').hide();
        
        SubscriptionsRequestor.getSubscriptions(response.subscriptions_uri);
        UsagesRequestor.getUsages(response.usages_uri);
        BillingRequestor.getConsumptions(response.consumptions_uri);
        
        if(response.contact){
            $('#user-contact-name').val(response.contact.name);
            $('#user-contact-email').val(response.contact.email);
            $('#user-contact-phone').val(response.contact.phone);
            $('#user-contact-company').val(response.contact.company);
        }
        
        var plan = BillingPlans.getPlan(response.plan);
        plan.stripe_id ? $('#plan-stripe').show() : $('#plan-stripe').hide();
        $('#user-plan-button-'+plan.name).button('toggle');
        $('#user-plan-monthly').val(plan.monthly);
        $('#user-plan-limit').val(plan.limit);
        $('#user-plan-overage').val(plan.overage);
        
        $('#user-modal .form-actions button').attr('data-uri', uri)
        
        $('#user-modal-header').text(response.username);
        $('#user-modal').modal('show');
    },
        
    updateUser: function(element){
        var uri = $(element).attr('data-uri');
        var form = $(element).attr('data-form');
        var params = $(form).serialize();
        UsersRequestor.updateUser(uri, params);
    },
    
    prepAddUser: function(){
        $('#user-modal-header').text('New User');
        $('#user-modal form .form-actions').hide();
        $('#user-modal-username').show();
        $('#user-modal-add-button').show();
        $('#user-modal').modal('show');
    },
    
    addUser: function(){
        var forms = $('#user-modal form');
        var params = forms.map(function(i){
            return $(forms[i]).serialize();
        }).toArray().join('&');
        var username = $('#user-basic-username').val();
        UsersRequestor.addUser(username, params);
    }
};

var UsersRequestor = {  
    getUsers: function(){
        $.ajax({
            url:encodeURIComponent('/services/users'),
            type:'GET',
            dataType:'json',
            success:UsersManager.populateUsersTable
        });
    },
    
    manageUser: function(uri, action){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'POST',
            data:'action='+action,
            dataType:'json',
            success:UsersRequestor.getUsers
        });
    },
    
    removeUser: function(uri){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'GET',
            dataType:'json',
            success:function(response){
                SubscriptionsRequestor.removeSubscriptions(response.subscriptions_uri);
            }
        });
        $.ajax({
            url:encodeURIComponent(uri),
            type:'DELETE',
            dataType:'json',
            success:UsersRequestor.getUsers
        });
    },
    
    getUser: function(uri){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'GET',
            dataType:'json',
            success:function(response){
                UsersManager.populateUserModal(uri, response);
            }
        });
    },
    
    updateUser: function(uri, params){
        $.ajax({
            url:encodeURIComponent(uri),
            type:'POST',
            data:params,
            dataType:'json',
            success:function(response){
                $('#user-modal').modal('hide');
                UsersRequestor.getUsers();
            }
        });
    },
    
    addUser: function(username, params){
        $.ajax({
            url:encodeURIComponent('/services/users/'+username),
            type:'PUT',
            data:params,
            dataType:'json',
            success:function(response){
                $('#user-modal').modal('hide');
                UsersRequestor.getUsers();
            }
        });
    }
};

var disableSubmissions = function(){
    $('#user-modal form').keydown(function(event){
        if(event.keyCode == 13){
            event.preventDefault();
            return false;
        }
    });
    $('#user-modal form').submit(function(event){
        event.preventDefault();
        return false;
    });
};

$(document).ready(function(){
    UsersManager.initialize();
    $('#user-modal').modal('hide');
    disableSubmissions();
});