angular.module('webui.datetime', [
    'core',
]);

angular.module('webui.datetime').run(customization => customization.plugins.datetime = {});

angular.module('webui.datetime').directive('neutralTimezone', () =>
    ({
        restrict: 'A',
        priority: 1,
        require: 'ngModel',
        link(scope, element, attrs, ctrl) {
            ctrl.$formatters.push(function(value) {
                let date = new Date(Date.parse(value));
                date = new Date(date.getTime() + (60000 * new Date().getTimezoneOffset()));
                return date;
            });

            ctrl.$parsers.push(value => new Date(value.getTime() - (60000 * new Date().getTimezoneOffset())));
        }
    })
);
