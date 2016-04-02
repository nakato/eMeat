angular.module('eMeatApp', []).controller('eMeatController', function($scope, $sce, $http) {
    var eMeat = this;

    eMeat.attendees = [];

    eMeat.availableAdds = [
        {id: 0, name: '0'},
        {id: 1, name: '1'},
        {id: 2, name: '2'},
        {id: 3, name: '3'},
        {id: 4, name: '4'},
    ];
    eMeat.attPluss = {id: '0', name: '0'}

    $scope.refresh = function() {
        eMeat.attendees = [];
        $http.get('api/get_attendees').then(function(response) {
            var rsp = response.data;
            angular.forEach(rsp, function(v, k) {
                eMeat.attendees.push({name: k, pluss: v});
            });
        });
    }

    $scope.refresh();

    eMeat.addAttendee = function() {
        var data = {"attendee":  eMeat.attName, "additions": eMeat.attPluss.id };
        console.log(data)
        var config = {};
        $http.post('api/add_attendee', data, config);
        eMeat.attName = "";
        eMeat.attPluss = {id: '0', name: '0'}
        $scope.refresh();
    };


    eMeat.title = "Me no know";
    eMeat.discription = "";
    $scope.discription = $sce.trustAsHtml(eMeat.discription);
    eMeat.add_description = function() {
        $http.get('api/get_discription').then(function(resp) {
            var title = resp.data.title;
            var discription = resp.data.discription;
            eMeat.title = title;
            eMeat.discription = discription;
            $scope.discription = $sce.trustAsHtml(eMeat.discription);
        });
    };

    eMeat.add_description();

});
