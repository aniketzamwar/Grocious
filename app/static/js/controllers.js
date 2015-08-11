var grociousControllers= angular.module('grociousApp.grociousControllers', []);

grociousControllers.controller('CategoryCtrl',function( $http , $scope ) {
    $http.get( '/getCategories' ).success( function( data ){
        console.log(data);
        $scope.categories = data;
    });
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
  this.search = function($page) {

    $http.get('/search?query=' + store.query + "&p=" + $page).success(function(data) {
      console.log(data)
      store.products = angular.fromJson(data.products);
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
    //href = href + "/" + count;
    $http.get('/cart/add/'+id+'/'+count).success(function(data) {
      alert("Item added to cart");
    });
  };

  this.getLink = function(id) {
    return "/cart/add/" + id;
  };
});
