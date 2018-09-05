angular.module('webui.auth.users', [
    'core',
]);

angular.module('webui.auth.users').run((customization) => {
    customization.plugins.auth_users = {
        forceUID: null
    };
});
