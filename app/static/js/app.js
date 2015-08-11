var app = angular.module('grociousApp',[
  'ngRoute',
  'grociousApp.grociousControllers'
  ]);

app.config(['$routeProvider','$provide', '$httpProvider',
    function($routeProvider) {
        $routeProvider.
            when('/', {
                templateUrl: '/static/templates/home-page.html',
                controller: 'StoreCtrl',
                controllerAs: 'store'
            }).
            otherwise({
                redirectTo: '/'
            });
    }
]);
