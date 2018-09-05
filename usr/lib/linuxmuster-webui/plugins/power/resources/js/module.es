angular.module('webui.power', [
    'core',
]);

angular.module('webui.power').run((customization) => {
    customization.plugins.power = {};
    customization.plugins.power.hideBatteries = false;
    customization.plugins.power.hideAdapters = false;
});
