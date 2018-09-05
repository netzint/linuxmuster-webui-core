angular.module('core').service('feedback', function($log, webuiVersion, webuiPlatform, webuiPlatformUnmapped) {
    this.enabled = true; // TODO
    this.token = 'df4919c7cb869910c1e188dbc2918807';

    this.init = () => {
        mixpanel.init(this.token);
        mixpanel.register({
            version: webuiVersion,
            platform: webuiPlatform,
            platformUnmapped: webuiPlatformUnmapped
        });
    };

    this.emit = (evt, params) => {
        if (this.enabled) {
            try {
                mixpanel.track(evt, params || {});
            } catch (e) {
                $log.error(e);
            }
        }
    };

    return this;
});
