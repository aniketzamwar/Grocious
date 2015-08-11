var app = angular.module('grociousApp',[
  'ngRoute',
  'grociousApp.grociousControllers'
  ]);

app.config(['$routeProvider',
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
