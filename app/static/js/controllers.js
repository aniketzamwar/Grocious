var grociousControllers= angular.module('grociousApp.grociousControllers', []);


grociousControllers.controller('ProductCtrl', function($scope, $routeParams, $http) {
    $http.get('/product/' + $routeParams.pId).success(function(data) {
      $scope.product = angular.fromJson(data.product);
    });

    $scope.add = function(id, count) {
      $http.get('/cart/add/' + id + '/' + count).success(function(data) {
        $scope.$root.cartCount = data.cartCount;
        $.toaster({ priority : 'success', message : data.message });
      });
    };
});

grociousControllers.controller('HeaderCtrl', function($scope){
  $scope.$root.cartCount = 0;
});

grociousControllers.controller('CartCheckoutCtrl', function($http, $scope){
        // create a blank object to hold our form information
  			// $scope will allow this to pass between controller and view
  			$scope.deliveryInfo = {};
        $scope.shippingOptions = [];
        $scope.products = [];

        // process the form
        $scope.submitShippingForm = function() {
  				console.log($scope.deliveryInfo);
          $http({
  			        method  : 'POST',
  			        url     : '/cart/checkout/',
  			        data    : $.param($scope.deliveryInfo),  // pass in data as strings
  			        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }  // set the headers so angular passing info as form data (not request payload)
  			    }).success(function(data) {
  			            console.log(data);
  			            if (!data.success) {
  			            	  // if not successful, bind errors to error variables
  			                $scope.errorName = data.errors.name;
  			            } else {
  			            	  // if successful, bind success message to message
  			                $scope.message = data.message;
                        $scope.products = data.products;
                        $scope.shippingOptions = data.shippingOptions;
                        $scope.selectedShippingOption = data.shippingOptions[0];
  			            }
  			    });
  			};

});

grociousControllers.controller('CartCtrl', function($http,$scope){

  $scope.getCart = function(){
    $http.get( '/getCart' ).success( function( data ){
        $scope.products = data.products;
    });
  }

  $scope.getCart();

  $scope.removeItem = function(id, count){
    $http.get("/cart/delete/" + id).success(function( data ){
      delete $scope.products[id];
      if($.isEmptyObject($scope.products)){
        $scope.products = null;
      }
      $scope.$root.cartCount = data.cartCount;
      $.toaster({ priority : 'warning', message : data.message });
    });
  }

  $scope.updateItem = function(id, count){
    $http.get("/cart/update/"+ id + "/" + count).success(function( data ){
      $scope.$root.cartCount = data.cartCount;
      $scope.products[id].count = count;
      $.toaster({ priority : 'info', message : data.message });
    });
  }

});


grociousControllers.controller('StoreCtrl',function ($http, $location, $log, $scope) {
  var store = this;
  this.products =  [];
  this.default = 1
  this.prev = -1
  this.next = -1
  this.notNext = true
  this.notPrev = true
  this.query = "";
  $scope.categoryId = "global";

  $http.get( '/getCategories/' ).success( function( data ){
      $scope.categories = data;
  });

  $scope.filter = function(category_id){
    console.log(category_id);
    $scope.categoryId = category_id;
    $scope.search(store.default);
  };

  $scope.search = function($page) {
    $http.get('/search/' + $scope.categoryId + "/" + $page + "/" + store.query).success(function(data) {
      console.log(data)
      store.products = angular.fromJson(data.products);
      $scope.$root.cartCount = data.cartCount;
      if (typeof data.next !== 'undefined') {
        store.next = data.next;
        store.notNext = false;
      } else {
        store.notNext = true;
      }
      if (typeof data.prev !== 'undefined') {
        store.prev = data.prev;
        store.notPrev = false;
      } else {
        store.notPrev = true;
      }
    });
  };

  $scope.add = function(id, count) {
    $http.get('/cart/add/' + id + '/' + count).success(function(data) {
      $scope.$root.cartCount = data.cartCount;
      $.toaster({ priority : 'success', message : data.message });
    });
  };
});
