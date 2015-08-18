var grociousFilters= angular.module('grociousApp.grociousFilters', []);

grociousFilters.filter('getTotalPrice', function() {
    return function(items) {
        var total = 0, i = 0;
        for (i = 0; i < items.length; i++) {
            total += items[i].price * items[i].count;
        }
        return total;
    }
});
