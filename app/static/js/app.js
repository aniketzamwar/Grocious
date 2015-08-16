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
            when('/mycart',{
              templateUrl: '/static/templates/cart-page.html',
              controller: 'CartCtrl',
            }).
            when('/product/:pId',{
              templateUrl: '/static/templates/product-page.html',
              controller: 'ProductCtrl',
            }).
            otherwise({
                redirectTo: '/'
            });
    }
]);
