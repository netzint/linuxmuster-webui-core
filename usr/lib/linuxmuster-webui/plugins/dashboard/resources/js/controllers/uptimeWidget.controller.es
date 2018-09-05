angular.module('webui.dashboard').controller('UptimeWidgetController', ($scope) => {
    $scope.$on('widget-update', ($event, id, data) => {
        if (id !== $scope.widget.id) {
            return;
        }
        $scope.uptime = data;
    })
});
