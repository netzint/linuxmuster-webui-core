angular.module('core').controller('CoreRootController', function($scope, $rootScope, $location, $localStorage, $log, $timeout, $q, identity, customization, urlPrefix, webuiPlugins, webuiVersion, webuiPlatform, webuiPlatformUnmapped, favicon, locale, config) {
    $rootScope.identity = identity;
    $rootScope.$location = $location;
    $rootScope.location = location;
    $rootScope.urlPrefix = urlPrefix;
    //$rootScope.feedback = feedback;
    $rootScope.webuiVersion = webuiVersion;
    $rootScope.webuiPlugins = webuiPlugins;
    $rootScope.customization = customization;

    // todo figure this out, used in settings template
    $rootScope.keys = function(x) { if (x) { return Object.keys(x); } else { return []; } };

    console.group('Welcome');
    console.info('Webui', webuiVersion);
    console.log('Running on', webuiPlatform, '/', webuiPlatformUnmapped);
    if (urlPrefix) {
        console.log('URL prefix', urlPrefix);
    }
    console.log('Plugins', webuiPlugins);
    console.groupEnd();

    $scope.navigationPresent = $location.path().indexOf('/view/login') === -1;

    //feedback.init();

    // ---

    $scope.showSidebar = angular.isDefined($localStorage.showSidebar) ? $localStorage.showSidebar : true
    $rootScope.toggleNavigation = (state) => {
        if (angular.isDefined(state)) {
            $scope.showSidebar = state;
        } else {
            $scope.showSidebar = !$scope.showSidebar;
        }
        $localStorage.showSidebar = $scope.showSidebar;
        $scope.$broadcast('navigation:toggle');
    };

    // ---
    $scope.showOverlaySidebar = false
    $rootScope.toggleOverlayNavigation = (state) => {
        if (angular.isDefined(state)) {
            $scope.showOverlaySidebar = state
        } else {
            $scope.showOverlaySidebar = !$scope.showOverlaySidebar
        }
        $scope.$broadcast('navigation:toggle')
    }

    $scope.$on('$routeChangeSuccess', function() {
        $scope.toggleOverlayNavigation(false)
        //feedback.emit('navigation', {url: $location.path()});
    })

    // ---

    $scope.isWidescreen = angular.isDefined($localStorage.isWidescreen) ? $localStorage.isWidescreen : true

    $scope.toggleWidescreen = function(state) {
        if (angular.isDefined(state)) {
            $scope.isWidescreen = state;
        } else {
            $scope.isWidescreen = !$scope.isWidescreen;
        }
        $localStorage.isWidescreen = $scope.isWidescreen;
        $scope.$broadcast('widescreen:toggle');
    };

    // ---

    identity.init();
    identity.promise.then(function() {
        $log.info('Identity', identity.user);
        return $rootScope.appReady = true;
    });

    favicon.init();

    setTimeout(() =>
        $(window).resize(() => {
            $scope.$apply(() => $rootScope.$broadcast('window:resize'))
        })
    );
});
