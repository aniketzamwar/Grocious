var grociousFilters= angular.module('grociousApp.grociousFilters', []);

grociousFilters.filter('getTotalPrice', function() {
    return function(items) {
        var total = 0, i = 0;
        for (key in items) {
            total += items[key].price * items[key].count;
        }
        return total;
    }
});
