angular.module('webui.settings', [
    'core',
    'webui.filesystem',
    'webui.passwd',
]);

angular.module('webui.settings').run(customization =>
    customization.plugins.settings = {}
);
