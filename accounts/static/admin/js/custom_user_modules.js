(function($) {
    .ready(function() {

        function updateGroupsAndPermissions() {
            var moduleSelect = #id_modules;
            var selectedModules = moduleSelect.val(); // array of selected module IDs

            if (!selectedModules || selectedModules.length === 0) return;

            // Call admin endpoint to fetch linked groups & permissions
            $.ajax({
                url: '/admin/accounts/systemmodule/module-data/',
                data: { ids: selectedModules.join(',') },
                success: function(data) {
                    // Update groups
                    #id_groups option.each(function() {
                        if (data.groups.includes(parseInt(.val()))) {
                            .prop('selected', true);
                        } else {
                            .prop('selected', false);
                        }
                    });

                    // Update permissions
                    #id_user_permissions option.each(function() {
                        if (data.permissions.includes(parseInt(.val()))) {
                            .prop('selected', true);
                        } else {
                            .prop('selected', false);
                        }
                    });
                }
            });
        }

        // Initial update
        updateGroupsAndPermissions();

        // Update whenever module selection changes
        #id_modules.change(updateGroupsAndPermissions);
    });
})(django.jQuery);
