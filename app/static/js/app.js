var app = angular.module('grociousApp',[
  'ngRoute',
  'grociousApp.grociousControllers',
  'grociousApp.grociousFilters'
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
            when('/checkout',{
              templateUrl: '/static/templates/checkout-page.html',
              controller: 'CartCheckoutCtrl',
            }).
            when('/orderInfo/:oId',{
              templateUrl: '/static/templates/order-info-page.html',
              controller: 'OrderInfoCtrl',
            }).
            when('/myOrders',{
              templateUrl: '/static/templates/my-orders-page.html',
              controller: 'OrdersCtrl',
            }).
            otherwise({
                redirectTo: '/'
            });
    }
]);
